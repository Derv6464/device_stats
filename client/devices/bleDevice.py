from client.devices.baseDevice import BaseDevice
from client.metrics.ble_data import BLE_Data
import simplepyble
import time
import array

class BLE_Device(BaseDevice):
    def __init__(self, logger, name, ble_data: BLE_Data, sample_rate=0.3):
        super().__init__(logger, name, ble_data.service_id)
        self.ble_data = ble_data
        self.client = None
        self.connected = False
        self.sample_rate = sample_rate
        self.start_time_ble = 0
        self.start_time_setup = 0
        self.sending_allowed = False

    def setup(self):
        adapters = simplepyble.Adapter.get_adapters()
        adapter = adapters[0]
        adapter.set_callback_on_scan_start(lambda: print("Scan started."))
        adapter.set_callback_on_scan_stop(lambda: print("Scan complete."))

        adapter.scan_for(5000)
        peripherals = adapter.scan_get_results()
        for peripheral in peripherals:
            if peripheral.identifier() == self.ble_data.target_device_name_id:
                target_peripheral = peripheral
                break
    
        target_peripheral.connect()
        self.client = target_peripheral
        time_ble = self.client.read(self.ble_data.service_id, self.ble_data.time_id)
        self.start_time_ble = array.array('H',time_ble)[0]
        self.start_time_setup = time.time()

    def run(self):
        try:
            while self.running:
                if self.client is not None and self.client.is_connected():
                    data = self.client.read(self.ble_data.service_id, self.ble_data.read_id)
                    data = self.parse_data(data)
                    #self.logger.info(data)
                    #self.logger.info("Trying to ack")
                    if data is not None:
                        self.send_ack()
                        self.sort_data(data)
                time.sleep(self.sample_rate)
        except Exception as e:
            self.logger.error(e)
        finally:
            self.cleanup()
            self.client.disconnect()
            self.logger.info("Shutdown Safely")

    def parse_data(self, frame: bytes):
        if len(frame) < 4:  
            print("Invalid frame length")
            return None

        numbers = list(array.array('H',frame))

        start_marker = numbers[0]
        payload = numbers[3:-1]
        checksum = numbers[-1]

        if start_marker != 0xA1:
            print("Invalid start marker")
            return None

        computed_checksum = 0
        for b in payload: 
            computed_checksum ^= b

        values = []
        if computed_checksum == checksum:
            for i in range(0,len(payload)-2,3):
                frame = {
                    "pot" : payload[i],
                    "isr" : payload[i+1],
                    "sampled_time" : payload[i+2]
                }
                values.append(frame)

            return values

    def send_ack(self):
        self.client.write_request(self.ble_data.service_id, self.ble_data.ack_id,  str.encode('A'))

    def sort_data(self, data):
        for frame in data:
            for metric in self.metrics:
                if metric.name in frame:
                    metric.get_value(frame[metric.name], 
                                    self.get_time(frame['sampled_time']))
                if metric.name == "isr":
                    self.sending_allowed = bool(frame[metric.name])

    def get_time(self, sample_time):
        offset = sample_time - self.start_time_ble
        real_time = self.start_time_setup + offset
        return real_time
    
    def send_data(self, data):
        self.client.write_request(self.ble_data.service_id, self.ble_data.write_id,str.encode(data))
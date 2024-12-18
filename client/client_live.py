from helpers.logger import Logger_Helper
from helpers.config import Config_Helper

from client.devices.laptop import Laptop
from client.devices.bleDevice import BLE_Device

from client.metrics.datamodel import MetricMaker
from client.metrics.standardMetric import StandardMetric
from client.metrics.bleMetric import BLE_Metric
from client.metrics.ble_data import BLE_Data

from threading import Thread
import time
import psutil
import socketio

class ClientLive:   
    def __init__(self):
        self.config = Config_Helper('config.json')
        Logger_Helper.setUp(self.config.get('logs_location'))
        self.logger = Logger_Helper.logger

        self.url = f"{self.config.get('client.url')}/upload"
        self.url_live = f"{self.config.get('client.url')}"

        self.sio = socketio.Client()
        self.setupSocket()
        try:
            self.setup()
        except Exception as e:
            self.logger.error("Failed to setup client")
            self.logger.error(e)
            exit(1)
       

    def setup(self):
        laptopMetrics = [
            StandardMetric('cpu', '%', psutil.cpu_percent),
            StandardMetric ('ram', '%', lambda: psutil.virtual_memory().percent)
        ]

        bleMetrics = [
            BLE_Metric('pot', 'V'),
            BLE_Metric('isr', 'bool')
        ]
        ble_data = BLE_Data("00000180-0000-1000-8000-00805f9b34fb", 
                            "0000fef4-0000-1000-8000-00805f9b34fb", 
                            "0000accc-0000-1000-8000-00805f9b34fb",
                            "0000daca-0000-1000-8000-00805f9b34fb", 
                            "0000113e-0000-1000-8000-00805f9b34fb", 
                            "Dervla BLE")


        self.fb = BLE_Device(self.logger, "FireBeetle", ble_data, 1)
        self.devices = [Laptop(self.logger, "MacBook", 1), 
                   self.fb
                   ]
        for device in self.devices:
            if isinstance(device, Laptop):
                device.add_metrics(laptopMetrics)
                device.setup()
            elif isinstance(device, BLE_Device):
                device.add_metrics(bleMetrics)

        for device in self.devices:
            device.setup()

        self.maker = MetricMaker(self.devices)

    def run_devices(self):
        for device in self.devices:
            device.start()

    def setupSocket(self):
        @self.sio.event
        def connect():
            print("Connected to server")

        @self.sio.on('colours')
        def handle_colours(data):
            print("Received data:", data)
            if self.fb.sending_allowed:
                self.fb.send_data(data.upper())

        @self.sio.event
        def disconnect():
            print("Disconnected from server")

    def run(self):
        try:        
            self.sio.connect(self.url_live)
            thread = Thread(target = self.run_devices)
            thread.start()
            time.sleep(1)

            while True:
                data = self.maker.make_single_metric()
                self.sio.emit('upload', data)  
                time.sleep(0.5)
        except KeyboardInterrupt:
            print("Exiting...")
            
            exit(0)
        except Exception as e:
            self.logger.error(e)
            exit(1)
        finally:
            self.sio.disconnect()
            if self.devices:
                for device in self.devices:
                    device.cleanup()
                    device.join()

            thread.join()


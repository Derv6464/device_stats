class BLE_Data:
    def __init__(self, service, read, ack, write,time, target_device_name):
        self.service_id = service
        self.read_id = read
        self.ack_id = ack
        self.write_id = write
        self.time_id = time
        self.target_device_name_id = target_device_name

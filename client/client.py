from helpers.logger import Logger_Helper
from helpers.config import Config_Helper

from client.devices.laptop import Laptop
from client.devices.bleDevice import BLE_Device

from client.metrics.datamodel import MetricMaker
from client.metrics.standardMetric import StandardMetric
from client.metrics.bleMetric import BLE_Metric
from client.metrics.ble_data import BLE_Data

import threading
import time
import requests
import psutil

class Client:   
    def __init__(self):
        self.config = Config_Helper('config.json')
        Logger_Helper.setUp(self.config.get('logs_location'))
        self.logger = Logger_Helper.logger

        self.url = f"{self.config.get('client.url')}/upload"

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


        self.devices = [Laptop(self.logger, "MacBook", 1), 
                   BLE_Device(self.logger, "FireBeetle", ble_data, 1)
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

    def make_request(self):
        data = self.maker.make_metrics()
        response = requests.post(self.url, json=data)
        if response.status_code == 200:
            self.maker.clear_metrics()
        #self.logger(response.text)

    def run_devices(self):
        for device in self.devices:
            device.start()

    def run(self):
        try:        
            thread = threading.Thread(target = self.run_devices)
            thread.start()
            time.sleep(1)

            while True:
                self.logger.info('Making request...')
                self.make_request()
                time.sleep(2)

        except KeyboardInterrupt:
            print("Exiting...")
            exit(0)
        except Exception as e:
            self.logger.error(e)
            exit(1)
        finally:
            if self.devices:
                for device in self.devices:
                    for thread in threading.enumerate(): 
                        print(thread.name)

                    device.cleanup()
                    device.join()

            

            thread.join()

            for thread in threading.enumerate(): 
                print(thread.name)
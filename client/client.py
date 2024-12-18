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
import requests
import json
import psutil




try:
    config = Config_Helper('config.json')
    print(config.get('logs_location'))
    Logger_Helper.setUp(config.get('logs_location'))
    logger = Logger_Helper.logger

    url = f"{config.get('client.url')}/upload"

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
    
    logger.info('This is an info message')

    #FireBeetle(logger),

    devices = [Laptop(logger, "MacBook", 1), 
               BLE_Device(logger, "FireBeetle", ble_data, 1)
               ]
    
    for device in devices:
        if isinstance(device, Laptop):
            device.add_metrics(laptopMetrics)
            device.setup()
        elif isinstance(device, BLE_Device):
            device.add_metrics(bleMetrics)

    for device in devices:
        device.setup()

    

    maker = MetricMaker(devices)

    def run():
        for device in devices:
            device.start()

    def make_request():
        data = maker.make_metrics()
        response = requests.post(url, json=data)
        if response.status_code == 200:
            maker.clear_metrics()
        print(response.text)

    thread = Thread(target = run)
    thread.start()
    time.sleep(1)

    while True:
        logger.info('Making request...')
        make_request()
        time.sleep(2)

except KeyboardInterrupt:
    print("Exiting...")
    if devices:
        for device in devices:
            device.cleanup()
            device.join()
            
    thread.join()
    exit(0)
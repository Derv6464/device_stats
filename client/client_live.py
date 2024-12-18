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
import socketio

config = Config_Helper('config.json')

print(config.get('logs_location'))
Logger_Helper.setUp(config.get('logs_location'))
logger = Logger_Helper.logger

url_live = f"{config.get('client.url')}"
url = f"{config.get('client.url')}/upload"

logger.info('Setting up metrics...')
laptopMetrics = [
    StandardMetric('cpu', '%', psutil.cpu_percent),
    StandardMetric ('ram', '%', lambda: psutil.virtual_memory().percent)
]

bleMetrics = [
    BLE_Metric('pot', 'V'),
    BLE_Metric('isr', 'bool')
]

logger.info('Setting up BLE data...')
ble_data = BLE_Data("00000180-0000-1000-8000-00805f9b34fb", 
                        "0000fef4-0000-1000-8000-00805f9b34fb", 
                        "0000accc-0000-1000-8000-00805f9b34fb",
                        "0000daca-0000-1000-8000-00805f9b34fb", 
                        "0000113e-0000-1000-8000-00805f9b34fb", 
                        "Dervla BLE")


logger.info('Setting up devices...')
mac = Laptop(logger, "MacBook", 1)
fb = BLE_Device(logger, "FireBeetle", ble_data, 1)
devices = [mac, fb]

for device in devices:
    if isinstance(device, Laptop):
        device.add_metrics(laptopMetrics)
        device.setup()
    elif isinstance(device, BLE_Device):
        device.add_metrics(bleMetrics)

for device in devices:
    try:
        device.setup()
    except Exception as e:
        logger.error(f"Error setting up device: {device.name}")
        logger.error(e)

maker = MetricMaker(devices)

def run():
    for device in devices:
        try:
            device.start()
        except Exception as e:
            logger.error(f"Error starting device: {device.name}")
            logger.error(e)


sio = socketio.Client()

@sio.event
def connect():
    print("Connected to server")

@sio.on('colours')
def handle_colours(data):
    print("Received data:", data)
    if fb.sending_allowed:
        fb.send_data(data.upper())

@sio.event
def disconnect():
    print("Disconnected from server")


sio.connect(url_live)

thread = Thread(target = run)
thread.start()
time.sleep(1)

try:
    while True:
        data = maker.make_single_metric()
        sio.emit('upload', data)  
        time.sleep(1)
except Exception as e:
    print(e)
    print("Exiting...")

finally:
    sio.disconnect()
    if devices:
        for device in devices:
            device.cleanup()
            device.join()
            
    thread.join()
    exit(0)


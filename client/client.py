from helpers.logger import Logger_Helper
from helpers.config import Config_Helper

from client.devices.laptop import Laptop
from client.devices.firebeetle import FireBeetle

from client.metrics.datamodel import MetricMaker
from client.metrics.baseMetric import Metric


from threading import Thread
import time
import requests
import json
import psutil

config = Config_Helper('config.json')

print(config.get('logs_location'))
Logger_Helper.setUp(config.get('logs_location'))
logger = Logger_Helper.logger

url = f"{config.get('client.url')}/upload"

cpu_metric = Metric('cpu', '%', psutil.cpu_percent)
ram_metric = Metric('ram', '%', lambda: psutil.virtual_memory().percent)

logger.info('This is an info message')
#FireBeetle(logger),
mac = Laptop(logger, "MacBook", 1)
mac2 = Laptop(logger, "MacBook2", 1)
devices = [mac, mac2]
mac.setup()
mac2.setup("fake_guid")

for device in devices:
    device.add_metric(cpu_metric)
    device.add_metric(ram_metric)


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


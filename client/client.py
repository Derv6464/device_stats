from helpers.logger import Logger_Helper
from helpers.config import Config_Helper

from client.devices.laptop import Laptop
from client.devices.firebeetle import FireBeetle
from client.devices.datamodel import MetricMaker

from client.metrics.cpu import CPU
from client.metrics.ram import RAM


from threading import Thread
import time
import requests
import json

config = Config_Helper('config.json')

print(config.get('logs_location'))
Logger_Helper.setUp(config.get('logs_location'))
logger = Logger_Helper.logger


cpu_metric = CPU(logger, 'cpu', '%')
ram_metric = RAM(logger, 'ram', '%')

logger.info('This is an info message')
#FireBeetle(logger),
mac = Laptop(logger, "MacBook")
mac2 = Laptop(logger, "MacBook2")
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
    #json_object = json.loads(data)
    json_formatted_str = json.dumps(data, indent=2)
    logger.info(json_formatted_str)
    response = requests.post('http://localhost:8000/upload', json=data)
    print(response.text)

thread = Thread(target = run)
thread.start()
time.sleep(1)
make_request() 

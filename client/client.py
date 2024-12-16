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


cpu_metric = Metric('cpu', '%', psutil.cpu_percent)
ram_metric = Metric('ram', '%', psutil.virtual_memory().percent)

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

from helpers.logger import Logger_Helper
from helpers.config import Config_Helper

from client.devices.laptop import Laptop
from client.devices.firebeetle import FireBeetle

import threading

config = Config_Helper('config.json')

print(config.get('logs_location'))
Logger_Helper.setUp(config.get('logs_location'))
logger = Logger_Helper.logger

logger.info('This is an info message')
#FireBeetle(logger),
devices = [Laptop(logger)]


def run():
    for device in devices:
        device.start()


from helpers.logger import Logger_Helper
from helpers.config import Config_Helper

config = Config_Helper('config.json')

print(config.get('logs_location'))
Logger_Helper.setUp(config.get('logs_location'))
logger = Logger_Helper.logger

logger.info('This is an info message')
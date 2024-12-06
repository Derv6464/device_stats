from helpers.logger import Logger_Helper
from helpers.config import Config_Helper

from flask import Flask, request, jsonify

config = Config_Helper('config.json')

print(config.get('logs_location'))
Logger_Helper.setUp(config.get('logs_location'))
logger = Logger_Helper.logger

logger.info('This is an info message')

app = Flask(__name__)
@app.route('/hello')
def hello_world():
    return 'Hello, World!'

@app.route('/data')
def data():
    return "metrics"

if __name__ == '__main__':
    app.run()
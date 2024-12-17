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
import socketio

config = Config_Helper('config.json')

print(config.get('logs_location'))
Logger_Helper.setUp(config.get('logs_location'))
logger = Logger_Helper.logger

url_live = f"{config.get('client.url')}"
url = f"{config.get('client.url')}/upload"

# client.py
cpu_metric = Metric('cpu', '%', psutil.cpu_percent)
ram_metric = Metric('ram', '%', lambda: psutil.virtual_memory().percent)
mac = Laptop(logger, "MacBook", 2)
devices = [mac]
mac.setup()
mac.add_metric(cpu_metric)
mac.add_metric(ram_metric)
maker = MetricMaker(devices)

# Create a SocketIO client instance
sio = socketio.Client()

# Event when the client connects to the server
@sio.event
def connect():
    print("Connected to server")
    #sio.send('Hello from Python client!')  # Send a message to the server

# Event when the client receives a message from the server
@sio.event
def message(data):
    print(data)

# Event when the client disconnects
@sio.event
def disconnect():
    print("Disconnected from server")

# Connect to the Flask-SocketIO server
sio.connect(url_live)

while True:
    data = maker.make_single_metric()
    json_formatted_str = json.dumps(data, indent=2)
    logger.info(json_formatted_str)
    
    sio.emit('upload', data)  # Send the data to the server
    time.sleep(0.2)


# Keep the client running
sio.wait()

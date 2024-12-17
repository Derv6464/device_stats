import threading
import time
from abc import ABC, abstractmethod
from datetime import datetime

from client.metrics.baseMetric import Metric

class BaseDevice(threading.Thread, ABC):
    def __init__(self, logger, name, guid=None, sample_rate=0.3):
        threading.Thread.__init__(self)
        self.running = True
        self.logger = logger

        self.name = name
        self.guid = guid

        self.sample_rate = sample_rate

        self.metrics = []

    def add_metric(self, metric: Metric):
        self.metrics.append(metric)

    @abstractmethod
    def setup(self):
       pass

    def run(self):
        while self.running:
            for metric in self.metrics:
                data = metric.get_value()
                #self.logger.info(data)

            time.sleep(self.sample_rate)

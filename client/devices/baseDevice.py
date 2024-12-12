import threading
import time
from abc import ABC, abstractmethod
from datetime import datetime

from client.metrics.baseMetric import BaseMetric

class BaseDevice(threading.Thread, ABC):
    def __init__(self, logger, name, guid=None):
        threading.Thread.__init__(self)
        self.running = True
        self.logger = logger

        self.name = name
        self.guid = guid

        self.metrics = []

    def add_metric(self, metric: BaseMetric):
        self.metrics.append(metric)

    @abstractmethod
    def setup(self):
       pass

    def run(self):
        while self.running:
            for metric in self.metrics:
                data = metric.get_value()
                self.logger.info(data)

            time.sleep(0.3)

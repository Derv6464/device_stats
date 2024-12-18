import threading
from abc import ABC, abstractmethod

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

    def add_metrics(self, metrics):
        self.metrics.extend(metrics)

    @abstractmethod
    def setup(self):
       pass

    @abstractmethod
    def run(self):
       pass

    def cleanup(self):
        self.logger.info(f"Cleaning up device: {self.name}")
        self.running = False 
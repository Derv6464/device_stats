import threading
import time
from abc import ABC, abstractmethod

class BaseDevice(threading.Thread, ABC):
    def __init__(self, logger):
        threading.Thread.__init__(self)
        self.running = True
        self.logger = logger

    @abstractmethod
    def read(self):
        pass

    def run(self):
        while self.running:
            data = self.read()
            self.logger.info(data)
            time.sleep(0.3)
from datetime import datetime
from abc import ABC, abstractmethod

class BaseMetric:
    def __init__(self, name, unit):
        self.name = name
        self.unit = unit
        self.values = []

    @abstractmethod
    def get_value(self):
        pass

    def clear_values(self):
        self.values = []

    def get_last_metric(self):
        return self.values[-1] if self.values else None
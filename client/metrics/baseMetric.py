from abc import ABC, abstractmethod


class BaseMetric(ABC):
    def __init__(self, name, unit):
        self.name = name
        self.unit = unit

        self.values = []

    @abstractmethod
    def get_value(self):
        pass

    def clear_values(self):
        self.values = []
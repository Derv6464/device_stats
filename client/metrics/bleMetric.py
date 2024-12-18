from datetime import datetime
from client.metrics.baseMetric import BaseMetric

class BLE_Metric(BaseMetric):
    def __init__(self, name, unit):
        super().__init__(name, unit)

    def get_value(self, value, time):
        value = {
            "value" : value,
            "sampled_time" : time
        }

        self.values.append(value)
        return value


from datetime import datetime
from client.metrics.baseMetric import BaseMetric

class StandardMetric(BaseMetric):
    def __init__(self, name, unit, function: callable):
        super().__init__(name, unit)
        self.function = function


    def get_value(self):
        value = {
            "value" : self.function(),
            "sampled_time" : datetime.now().timestamp()
        }

        self.values.append(value)
        return value

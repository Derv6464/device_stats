from  client.metrics.baseMetric import BaseMetric
import psutil
from datetime import datetime

class CPU(BaseMetric):
    def __init__(self, logger, name, unit):
        BaseMetric.__init__(self, name, unit)
        
    def get_value(self):
        value = {
            "value" : psutil.cpu_percent(),
            "sampled_time" : datetime.now().timestamp()
        }

        self.values.append(value)

        return value
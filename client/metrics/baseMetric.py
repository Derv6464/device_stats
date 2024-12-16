from datetime import datetime

class Metric:
    def __init__(self, name, unit, function: callable):
        self.name = name
        self.unit = unit
        self.function = function

        self.values = []

    def get_value(self):
        value = {
            "value" : self.function(),
            "sampled_time" : datetime.now().timestamp()
        }

        self.values.append(value)

        return value

    def clear_values(self):
        self.values = []
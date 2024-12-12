from datetime import datetime

class Device:
    def __init__(self, name, guid):
        self.name = name
        self.guid = guid

        self.metrics = []

    def add_metric_type(self, metric):
        self.metrics.append(metric)

    def add_metric_types(self, metrics):
        self.metrics.extend(metrics)

class Metric_Type:
    def __init__(self, name, unit):
        self.metric_type_name = name
        self.unit = unit

        self.values = []

    def add_value(self, metric):
        self.values.append(metric)

    def add_values(self, metrics):
        self.values.extend(metrics)


class Metric:
    def __init__(self,data):
        self.value = data.value
        self.sampled_time = data.sampled_time


class MetricMaker:
    def __init__(self, devices: list[Device]):
        self.devices = devices

    def make_metrics(self):
        send_time = datetime.now().timestamp()
        time_offset = datetime.now().astimezone().utcoffset().total_seconds() / 60
        data = {
            "devices": [
                {
                    "name": device.name,
                    "guid": device.guid,
                    "metrics": [
                        {
                            "metric_type": metric.name,
                            "unit": metric.unit,
                            "values": [
                                value for value in metric.values
                            ]
                        } for metric in device.metrics
                    ]
                } for device in self.devices
            ],
            "send_time": send_time,
            "time_offset": time_offset,
        }

        return data
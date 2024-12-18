from client.devices.baseDevice import BaseDevice
from datetime import datetime

class Metric_Type:
    def __init__(self, metrics):
        self.metric_type_name = metrics.metric_type
        self.unit = metrics.unit

        self.values = [Metric(metric) for metric in metrics.values]


class Metric:
    def __init__(self,data):
        self.value = data.value
        self.sampled_time = data.sampled_time


class MetricMaker:
    def __init__(self, devices: list[BaseDevice]):
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
    
    def clear_metrics(self):
        for device in self.devices:
            for metric in device.metrics:
                metric.clear_values()

    def make_single_metric(self):
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
                                metric.get_last_metric()
                            ]
                        } for metric in device.metrics
                    ]
                } for device in self.devices
            ],
            "send_time": send_time,
            "time_offset": time_offset,
        }

        return data
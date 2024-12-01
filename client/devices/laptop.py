from  client.devices.baseDevice import BaseDevice
import psutil

class Laptop(BaseDevice):
    def __init__(self, logger):
        BaseDevice.__init__(self, logger)
        

    def read(self):
        self.logger.info('Reading laptop data')
        return {
            'cpu': psutil.cpu_percent(),
            'memory': psutil.virtual_memory().percent,
            'disk': psutil.disk_usage('/').percent,
            'network': psutil.net_io_counters()
        }
from client.devices.baseDevice import BaseDevice

class FireBeetle(BaseDevice):
    def __init__(self, logger):
        BaseDevice.__init__(self, logger)

    def read(self):
        return "FireBeetle data"
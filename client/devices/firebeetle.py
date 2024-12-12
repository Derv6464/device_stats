from client.devices.baseDevice import BaseDevice

class FireBeetle(BaseDevice):
    def __init__(self, logger):
        BaseDevice.__init__(self, logger)

    def setup(self):
        #bluetooth setup
        pass
    
    def read(self):
        return "FireBeetle data"
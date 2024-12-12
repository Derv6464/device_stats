from  client.devices.baseDevice import BaseDevice
import psutil
import subprocess

class Laptop(BaseDevice):
    def __init__(self, logger, name):
        BaseDevice.__init__(self, logger, name)
        
    def setup(self, guid=None):
        self.logger.info('Setting up laptop')

        if guid is None:
            result = subprocess.run(
                ["system_profiler", "SPHardwareDataType"], capture_output=True, text=True
            )
        else:
            self.guid = guid
            self.logger.info(f"GUID: {self.guid}")
            return
        
        for line in result.stdout.splitlines():
            if "Hardware UUID" in line:
                self.guid = line.split(":")[1].strip()

        self.logger.info(f"GUID: {self.guid}")



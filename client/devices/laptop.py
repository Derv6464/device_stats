from  client.devices.baseDevice import BaseDevice
import subprocess
import time

class Laptop(BaseDevice):
    def __init__(self, logger, name, sample_rate=0.3):
        BaseDevice.__init__(self, logger, name)
        self.sample_rate = sample_rate
        
    def setup(self, guid=None):
        #self.logger.info('Setting up laptop')

        if guid is None:
            result = subprocess.run(
                ["system_profiler", "SPHardwareDataType"], capture_output=True, text=True
            )
        else:
            self.guid = guid
            #self.logger.info(f"GUID: {self.guid}")
            return
        
        for line in result.stdout.splitlines():
            if "Hardware UUID" in line:
                self.guid = line.split(":")[1].strip()

        #self.logger.info(f"GUID: {self.guid}")

    def run(self):
        try:
            while self.running:
                for metric in self.metrics:
                    data = metric.get_value()
                    #self.logger.info(data)

                time.sleep(self.sample_rate)
        except Exception as e:
            self.logger.error(e)
        finally:
            self.cleanup()
            self.logger.info("Shutdown Safely")

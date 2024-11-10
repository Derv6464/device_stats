import json
import os

class Config_Helper:
    def __init__(self, config_file):
        self.config_file = config_file
        self.config = self.load_config()

    def load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as file:
                return json.load(file)
        else:
            return {}

    def save_config(self):
        with open(self.config_file, 'w') as file:
            json.dump(self.config, file, indent=4)

    def get(self, key, default=None):
        return self.config[key] if key in self.config else default

    def set(self, key, value):
        self.config[key] = value
        self.save_config()

    def delete(self, key):
        if key in self.config:
            del self.config[key]
            self.save_config()

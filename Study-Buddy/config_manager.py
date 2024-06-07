import yaml

class ConfigManager:
  def __init__(self, config_path: str = "/home/buddy/Study-Buddy/Study-Buddy/config.yaml"):# "./Study-Buddy/config.yaml" ):
    print(f"GLOBAL ConfigManager init...\n. . . Loading config from {config_path}\n")
    self.config_path = config_path
    self._config = self.load_config()

  def load_config(self):
    try:
      with open(self.config_path, 'r') as file:
        return yaml.safe_load(file)
    except FileNotFoundError:
      raise FileNotFoundError(f"Config file not found at {self.config_path}")
    except yaml.YAMLError as e:
      raise Exception(f"Error loading config file: {e}")

  def get(self, key: str, default=None):
    return self._config.get(key, default)

config_manager = ConfigManager() # global instance
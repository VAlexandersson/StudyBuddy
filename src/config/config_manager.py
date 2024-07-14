import os
import yaml

class ConfigManager:
  def __init__(self, config_path: str = None):# "./Study-Buddy/config.yaml" ):
    if config_path is None:
      config_path = self._retrieve_config_path()

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

  def _retrieve_config_path(self):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, "config.yaml")

config_manager = ConfigManager() # global instance
import os
import yaml

class ConfigManager:
  def __init__(self, env:str, config_path: str = None):

    self.config_path = config_path or self._retrieve_config_path(env)

    print(f"GLOBAL ConfigManager init...\n. . . Loading config from {self.config_path}\n")
    
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

  def _retrieve_config_path(self, env: str):

    current_file_path = os.path.abspath(__file__)
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file_path)))
    return os.path.join(project_root, "config", env + ".yaml")
  

  def set_config(self, yaml_string: str, config_key: str = None):
    try:
      new_config = yaml.safe_load(yaml_string)
      if config_key:
        if config_key in self._config:
          self._config[config_key].update(new_config)
        else:
          self._config[config_key] = new_config
      else:
        self._config.update(new_config)
    except yaml.YAMLError as e:
      raise Exception(f"Error loading config from string: {e}")

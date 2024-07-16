import os
import yaml


class ConfigManager:
  def __init__(self, env: str = None, config_path: str = None):# "./Study-Buddy/config.yaml" ):

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

    # Navigate up to the project root directory
        # Navigate up to the project root directory
    current_file_path = os.path.abspath(__file__)
    project_root = os.path.dirname(os.path.dirname(current_file_path))
    print(f"BASE DIR: {project_root}")
    return os.path.join(project_root, "config", (env or "config") + ".yaml")


#config_manager = ConfigManager() # global instance
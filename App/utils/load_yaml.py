import yaml
import os

def load_yaml_config(file_name: str) -> dict:
    """Loads a YAML configuration files"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_folder = "config/"
    file_path = os.path.join(base_dir, config_folder, file_name)
    with open(file_path, 'r') as file:
        config = yaml.safe_load(file)
    return config
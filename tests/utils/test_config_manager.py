import pytest
from src.utils.config_manager import ConfigManager
import os

@pytest.fixture
def test_config_file(tmp_path):
    config_content = """
    TASKS:
      - name: "PreprocessQueryTask"
        class: src.tasks.preprocess_query.PreprocessQueryTask
        services:
          - text_generation
    ROUTING:
      PreprocessQueryTask:
        default: "ClassifyQueryTask"
    """
    config_file = tmp_path / "test_config.yaml"
    config_file.write_text(config_content)
    return str(config_file)

def test_config_manager_load(test_config_file):
    config = ConfigManager(config_path=test_config_file)
    assert config.get("TASKS")[0]["name"] == "PreprocessQueryTask"
    assert config.get("ROUTING")["PreprocessQueryTask"]["default"] == "ClassifyQueryTask"

def test_config_manager_missing_file():
    with pytest.raises(FileNotFoundError):
        ConfigManager(config_path="non_existent_file.yaml")

def test_config_manager_invalid_yaml(tmp_path):
    invalid_config = tmp_path / "invalid_config.yaml"
    invalid_config.write_text("{ invalid: yaml: content}")
    with pytest.raises(Exception):
        ConfigManager(config_path=str(invalid_config))
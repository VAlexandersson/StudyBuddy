# tests/conftest.py
import pytest
from src.utils.config_manager import ConfigManager

@pytest.fixture
def config():
    return ConfigManager()  # Assume this loads a test configuration

@pytest.fixture
def mock_text_generation_service():
    class MockService:
        def generate_text(self, prompt, system_prompt, temperature):
            return "This is a mock response"
    return MockService()

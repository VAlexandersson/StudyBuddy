from abc import ABC, abstractmethod
from typing import Any


class BaseLLM(ABC):
    @abstractmethod
    def generate_text(self, prompt: str, **kwargs) -> str:
        """Generates text using the LLM based on the given prompt."""
        pass

    @abstractmethod
    def format_prompt(self, user_prompt: str, sys_prompt: str) -> Any:
        """Formats the user and system prompts into a format suitable for the LLM."""
        pass


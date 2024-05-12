from abc import ABC, abstractmethod


class BaseLLM(ABC):
    @abstractmethod
    def generate_text(self, prompt: str, **kwargs) -> str:
        pass

    @abstractmethod
    def format_prompt(self, user_prompt: str, sys_prompt: str) -> str:
        pass
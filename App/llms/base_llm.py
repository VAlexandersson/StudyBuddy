from abc import ABC, abstractmethod


class BaseLLM(ABC):
    @abstractmethod
    def generate_text(self, prompt, **kwargs) -> str:
        """Generates text using the LLM based on the given prompt."""
        pass


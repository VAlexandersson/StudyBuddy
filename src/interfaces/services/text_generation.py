from abc import ABC, abstractmethod

class TextGenerationService(ABC):
  @abstractmethod
  async def generate_text(self, prompt: str, system_prompt: str, temperature: float) -> str:
    pass
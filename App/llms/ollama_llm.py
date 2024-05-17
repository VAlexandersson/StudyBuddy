import ollama import Client
from llms.base_llm import BaseLLM

class OllamaClient(BaseLLM):
    def __init__(self, model: str, host: str = 'http://localhost:11434'):
      self.model = model
      self.client = Client(host = host)

    def generate_text(self, prompt: str) -> str:
      
      generated_text = ollama.chat(model=self.model, messages=[
        {
          'role': 'user',
          'content': prompt,
        },
      ])
      
      return generated_text['message']['content']
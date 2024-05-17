import cohere
from llms.base_llm import BaseLLM

class CohereClient(BaseLLM):
  def __init__(self, api_key: str, model: str = "command-r-plus"):
    self.client = cohere.Client(api_key=api_key)
    self.model = model

  def generate_text(self, prompt: str, **kwargs) -> str:
    generated_text = self.client.chat(
      self.model,
      message=prompt
    )
    return generated_text

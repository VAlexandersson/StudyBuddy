
from src.rag_system import RAGSystem
from src.models.response import Response

class CommandLineUI:
  def __init__(self, rag_system: RAGSystem):
    self.rag_system = rag_system

  def get_input(self) -> str:
    return input("User: ")

  def post_output(self, response: Response):
    print(f"Assistant: {response.text}")

  def run(self):
    while True:
      user_input = self.get_input()
      if user_input.lower() in ['exit', 'quit']:
        break
      response = self.rag_system.process_query(user_input)
      self.post_output(response)
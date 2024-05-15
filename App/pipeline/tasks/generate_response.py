from pipeline.tasks import Task
from models.text_generation import LLM

class GenerateResponseTask(Task):
  def __init__(self):
    self.llm = LLM()
    
  def run(self, data):
    query = data["query"]
    filtered_documents = data["filtered_documents"]
    response = self.llm.generate_response(query, filtered_documents)
    return {
      "query": query, 
      "response": response, 
      "filtered_documents": filtered_documents, 
      "decomposed_query": data["decomposed_query"], 
      "classification": data["classification"]
    }
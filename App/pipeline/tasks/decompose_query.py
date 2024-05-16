from pipeline.tasks import Task
from models.text_generation import LLM

class DecomposeQueryTask(Task):
  def __init__(self):
    self.llm = LLM()

  def run(self, data):
    query = data["query"]

    
    decomposed_query = self.llm.generate_response(query, ["Decompose the query into its constituent parts."])

    return {
        "query": query, 
        "decomposed_query": decomposed_query, 
        "classification": data["classification"]
    }
    
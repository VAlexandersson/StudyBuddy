from pipeline.tasks import Task
from models.text_generation import LLM
from pprint import pprint

class GenerateResponseTask(Task):
  def __init__(self):
    self.llm = LLM()
    
  def run(self, data):
    
    query = data["query"]
    reranked_documents = data["reranked_documents"]
    pprint(reranked_documents)

    top_documents = [doc.document for doc in reranked_documents[:4]]

    context = "\n- ".join(top_documents)
    
    response = self.llm.generate_response(query, context=context)
    
    return {
      "query": query, 
      "response": response, 
      "reranked_documents": reranked_documents, 
      "decomposed_query": data["decomposed_query"], 
      "classification": data["classification"]
    }
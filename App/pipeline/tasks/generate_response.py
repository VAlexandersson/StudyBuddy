from config.prompt_library import STANDARD_PROMPT
from pipeline.tasks import Task
from models.text_generation import LLM
from pprint import pprint
from utils.concat_documents import concat_documents

class GenerateResponseTask(Task):
  def __init__(self):
    self.llm = LLM()
    
  def run(self, data):
    user, system = STANDARD_PROMPT
    
    query = data["query"]
    reranked_documents = data["reranked_documents"]
    grades = data["grades"]
    classifications = data["classification"]
    
    # pprint(reranked_documents)
    # top_documents = [doc.document for doc in reranked_documents[:4]]
    # context = "\n- ".join(top_documents)
    for i, doc in enumerate(reranked_documents):
      print(f"{i}( grade:{grades[i]} ):\n| Type:{classifications}\t{query}\n{doc.document}\n\n")
      
    context = concat_documents(reranked_documents)
    
    
    
    response = self.llm.generate_response(user.format(query, context), system)

    print("\n\nResponse: ", response)
    
    return {
      "query": query, 
      "response": response, 
      "reranked_documents": reranked_documents, 
      "decomposed_query": data["decomposed_query"], 
      "classification": data["classification"]
    }
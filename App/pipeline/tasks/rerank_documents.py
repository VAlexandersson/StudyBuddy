from pipeline.tasks import Task
from models.cross_encoder import ReRankerModel


class ReRankingTask(Task):
  def __init__(self):
    self.cross_encoder = ReRankerModel()

  def run(self, data, top_k=10):
    query = data["query"]
    documents = data["retrieved_documents"]

    query_doc_pairs = [(query, doc.document) for doc in documents]
    scores = self.cross_encoder.predict(query_doc_pairs)

    print(scores)

    combined = list(zip(scores, documents))

    print("Unsorted")
    for item in combined:
      print(f"Score: {round(item[0], 4)}\tDoc_ID: {item[1].id}")

    combined.sort(key=lambda x: x[0], reverse=True)

    print("\nSorted")
    for item in combined:
      print(f"Score: {round(item[0], 4)}\tDoc_ID: {item[1].id}")
      
    documents = [item[1] for item in combined]
    
    return {
      "query": query, 
      "reranked_documents": documents, 
      "decomposed_query": data["decomposed_query"], 
      "classification": data["classification"]
    }


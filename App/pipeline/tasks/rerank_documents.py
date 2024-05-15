from pipeline.tasks import Task
from models.cross_encoder import ReRankerModel

class ReRankingTask(Task):
  def __init__(self):
    self.cross_encoder = ReRankerModel()

  def run(self, data, top_k=10):
    query = data["query"]
    docs = data["retrieved_documents"]

    query_doc_pairs = [(query, doc) for doc in docs]

    print(docs)
    scores = self.cross_encoder.predict(query_doc_pairs)
    for i, doc in enumerate(docs):
      doc["score"] = scores[i]

    docs = sorted(docs, key=lambda x: x["score"], reverse=True)[:top_k]
    print(scores) 
    print(docs)
   
    print(f"ReRanking {len(scores)} documents.")
    #results = rerank_results.results
    #print(f"Reranked {len(results)} documents.")
    #reranked_docs_idx = [result.index for result in results]
    return docs


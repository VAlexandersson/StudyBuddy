from pipeline.tasks import Task
from models.cross_encoder import ReRankerModel
from pipeline.data_models import ReRankedDocuments, RetrievedDocuments


class ReRankingTask(Task):
  def __init__(self):
    self.cross_encoder = ReRankerModel()

  def run(self, retrieved_documents: RetrievedDocuments, top_k=10):
    query = retrieved_documents.query.text
    documents = retrieved_documents.documents

    query_doc_pairs = [(query, doc.document) for doc in documents]
    scores = self.cross_encoder.predict(query_doc_pairs)

    combined = list(zip(scores, documents))
    combined.sort(key=lambda x: x[0], reverse=True)
    
    documents = [item[1] for item in combined[:top_k]]
    
    return ReRankedDocuments(query=retrieved_documents.query, documents=documents)


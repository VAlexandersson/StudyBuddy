from pipeline.tasks import Task
from db.knowledge_base import VectorDB
from models.sentence_transformer import EmbeddingModel

class RetrieveDocumentsTask(Task):
  def __init__(self):
      self.sentence_transformer = EmbeddingModel()
      self.collection = VectorDB().get_collection()

  def run(self, data, top_k=10):
    query = data["query"]

    retrieved_documents = self.collection.query(
      query_embeddings=[self.sentence_transformer.encode(query)], 
      n_results=top_k
    )

    return {
      "query": query, 
      "retrieved_documents": retrieved_documents, 
      "decomposed_query": data["decomposed_query"], 
      "classification": data["classification"]
    }
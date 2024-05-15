from pipeline.tasks import Task
from db.knowledge_base import VectorDB
from objects.document import DocumentObject
from models.sentence_transformer import EmbeddingModel


class RetrieveDocumentsTask(Task):
  def __init__(self):
    self.sentence_transformer = EmbeddingModel()
    self.collection = VectorDB().get_collection()

  def run(self, data, top_k=10):
    query = data["query"]

    retrieved_documents = self.collection.query(
      query_embeddings=[
        self.sentence_transformer.encode(query)], 
      n_results=top_k
    )
    docs = retrieved_documents["documents"][0]
    ids = retrieved_documents["ids"][0]
    metadatas = retrieved_documents["metadatas"][0]
    documents = [DocumentObject(id=id, document=doc, metadatas=metadata) 
                     for id, doc, metadata in zip(ids, docs, metadatas)]

    return {
      "query": query, 
      "retrieved_documents": documents, 
      "decomposed_query": data["decomposed_query"], 
      "classification": data["classification"]
    }
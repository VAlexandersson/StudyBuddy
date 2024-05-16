from pipeline.tasks import Task
from db.knowledge_base import VectorDB
from models.sentence_transformer import EmbeddingModel
from pipeline.data_models import Query, DocumentObject, RetrievedDocuments


class RetrieveDocumentsTask(Task):
  def __init__(self):
    self.sentence_transformer = EmbeddingModel()
    self.collection = VectorDB().get_collection()

  def run(self, query: Query, top_k=10):


    # TODO if decomposed_query, retrieve documents for each part of the query
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

    return RetrievedDocuments(query=query, documents=documents)
# src/service/document_retrieval/chroma_retrieval.py
from typing import List
from src.models.document import DocumentObject

from src.interfaces.services.document_retrieval import DocumentRetrievalService
from src.interfaces.services.text_embedder import TextEmbeddingService

import chromadb

class ChromaDocumentRetrievalService(DocumentRetrievalService):
  def __init__(self, client: chromadb.Client, embedding_service: TextEmbeddingService):
    self.client = client
    self.embedding_service = embedding_service

  def get_relevant_documents(self, query: str, top_k: int = 10) -> List[DocumentObject]:
    query_embeddings = self.embedding_service.encode(query)
    collection = self.client.get_or_create_collection(name="course_documents")
    
    retrieved_documents = collection.query(
      query_embeddings=query_embeddings,
      n_results=top_k
    )

    return self._create_document_objects(retrieved_documents)

  def get_collection_documents(self, query: str, col_name: str, top_k: int = 10) -> List[DocumentObject]:
    query_embeddings = self.embedding_service.encode(query)
    collection = self.client.get_collection(col_name)
    
    retrieved_documents = collection.query(
      query_embeddings=query_embeddings,
      n_results=top_k
    )

    return self._create_document_objects(retrieved_documents)

  def _create_document_objects(self, retrieved_documents):
    docs = retrieved_documents["documents"][0]
    ids = retrieved_documents["ids"][0]
    metadatas = retrieved_documents["metadatas"][0]

    return [DocumentObject(id=id, document=doc, metadatas=metadata) 
      for id, doc, metadata in zip(ids, docs, metadatas)]
import logging
from typing import List
from src.models.document import DocumentObject
from src.interfaces.services.document_retrieval import DocumentRetrievalService
from src.interfaces.services.text_embedder import TextEmbeddingService
import chromadb
import asyncio

logger = logging.getLogger(__name__)

class ChromaDocumentRetrievalService(DocumentRetrievalService):
    def __init__(self, client: chromadb.Client, embedding_service: TextEmbeddingService):
        self.client = client
        self.embedding_service = embedding_service

    async def get_relevant_documents(self, query: str, top_k: int = 10) -> List[DocumentObject]:
        try:
            query_embeddings = await self.embedding_service.encode(query)
            logger.debug(f"Query embeddings shape: {len(query_embeddings)}")
            collection = self.client.get_or_create_collection(name="course_documents")
            
            loop = asyncio.get_event_loop()
            retrieved_documents = await loop.run_in_executor(
                None,
                self._query_collection,
                collection,
                query_embeddings,
                top_k
            )

            return await self._create_document_objects(retrieved_documents)
        except Exception as e:
            logger.error(f"Error in get_relevant_documents: {e}")
            raise

    async def get_collection_documents(self, query: str, col_name: str, top_k: int = 10) -> List[DocumentObject]:
        try:
            query_embeddings = await self.embedding_service.encode(query)
            logger.debug(f"Query embeddings shape: {len(query_embeddings)}")
            collection = self.client.get_collection(col_name)
            
            loop = asyncio.get_event_loop()
            retrieved_documents = await loop.run_in_executor(
                None,
                self._query_collection,
                collection,
                query_embeddings,
                top_k
            )

            return await self._create_document_objects(retrieved_documents)
        except Exception as e:
            logger.error(f"Error in get_collection_documents: {e}")
            raise

    def _query_collection(self, collection, query_embeddings, top_k):
        try:
            return collection.query(
                query_embeddings=query_embeddings,
                n_results=top_k
            )
        except Exception as e:
            logger.error(f"Error in _query_collection: {e}")
            raise

    async def _create_document_objects(self, retrieved_documents):
        try:
            docs = retrieved_documents["documents"][0]
            ids = retrieved_documents["ids"][0]
            metadatas = retrieved_documents["metadatas"][0]

            return [DocumentObject(id=id, document=doc, metadatas=metadata) 
                for id, doc, metadata in zip(ids, docs, metadatas)]
        except Exception as e:
            logger.error(f"Error in _create_document_objects: {e}")
            raise
from abc import ABC, abstractmethod
from typing import List
from src.models.document import DocumentObject

class DocumentRetrievalService(ABC):
    @abstractmethod
    async def get_relevant_documents(self, query: str, top_k: int = 10) -> List[DocumentObject]:
        pass

    @abstractmethod
    async def get_collection_documents(self, query: str, col_name: str, top_k: int = 10) -> List[DocumentObject]:
        pass
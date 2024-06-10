from abc import ABC, abstractmethod
from typing import List
from models.data_models import DocumentObject

class DocumentRetriever(ABC):
  @abstractmethod
  def get_relevant_documents(self, query: str, top_k: int = 10) -> List[DocumentObject]:
    """Retrieves relevant documents based on the query text.

    Args:
        query: The user's raw query text.
        top_k: The number of top documents to retrieve.

    Returns:
        A list of DocumentObject instances representing the retrieved documents.
    """
    pass
from abc import ABC, abstractmethod
from typing import List
from src.models.document import DocumentObject


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

  @abstractmethod
  def get_collection_documents(self, query: str, col_name: str, top_k: int = 10) -> List[DocumentObject]:
    """Retrieves relevant documents from a specific collection based on the query text.

    Args:
        query: The user's raw query text.
        col_name: The name of the collection to search.
        top_k: The number of top documents to retrieve.

    Returns:
        A list of DocumentObject instances representing the retrieved documents.
    """
    pass

class KnowledgeBase(DocumentRetriever):
  def _place_holder(self):
    raise NotImplementedError("This method is a placeholder and not yet implemented.")
from src.tasks import Task
from src.utils.logging_utils import logger
from src.models.context import Context
from src.models.document import RetrievedDocuments
from src.interfaces.services.document_retrieval import DocumentRetrievalService
from typing import Dict, Any

class RetrieveDocumentsTask(Task):
  def __init__(self, name: str, services: Dict[str, Any]):
    super().__init__(name, services)
    self.document_retrieval_service: DocumentRetrievalService = services['document_retrieval']

  def run(self, context: Context) -> Context:
    documents = self.document_retrieval_service.get_collection_documents( 
      context.query.text,
      col_name="nutrition_science",
      top_k=5
    )

    retrieved_documents = RetrievedDocuments(documents=documents)

    context.retrieved_documents = retrieved_documents
    logger.debug(f"Retrieved Documents: {retrieved_documents.get_text()}")
    return context
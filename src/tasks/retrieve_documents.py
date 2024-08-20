import logging
from src.tasks import Task
from src.models.context import Context
from src.models.document import RetrievedDocuments
from src.interfaces.services.document_retrieval import DocumentRetrievalService
from typing import Dict, Any

logger = logging.getLogger(__name__)

class RetrieveDocumentsTask(Task):
  def __init__(self, name: str, services: Dict[str, Any]):
    super().__init__(name, services)
    self.document_retrieval_service: DocumentRetrievalService = services['document_retrieval']

  async def run(self, context: Context) -> Context:
    try:
      documents = await self.document_retrieval_service.get_collection_documents( 
        query=context.query.text,
        col_name="nutrition_science",
        top_k=10
      )

      logger.info(f"Retrieved documents ID: {[doc.id for doc in documents]}")
      retrieved_documents = RetrievedDocuments(documents=documents)
      context.retrieved_documents = retrieved_documents
      
      return context
    except Exception as e:
      logger.error(f"Error in RetrieveDocumentsTask: {e}")
      context.error = str(e)
      return context
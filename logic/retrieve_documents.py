#from db.knowledge_base import VectorDB
from models.data_models import PipelineContext, RetrievedDocuments

from logging import Logger
from logic import Task

class RetrieveDocumentsTask(Task):
  def run(self, context: PipelineContext, logger: Logger) -> PipelineContext:

    documents = self.document_retriever.get_relevant_documents( 
      context.query.text, 
      top_k=10
    )

    retrieved_documents = RetrievedDocuments(documents=documents)
    
    context.retrieved_documents = retrieved_documents
    logger.debug(f"Retrieved Documents: {retrieved_documents.get_text()}")
    
    return context

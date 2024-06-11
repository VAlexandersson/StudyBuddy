from models.data_models import Context, RetrievedDocuments

from logging import Logger
from tasks import Task

class RetrieveDocumentsTask(Task):
  def run(self, context: Context, logger: Logger) -> Context:

    documents = self.document_retriever.get_relevant_documents( 
      context.query.text, 
      top_k=10
    )

    retrieved_documents = RetrievedDocuments(documents=documents)
    
    context.retrieved_documents = retrieved_documents
    logger.debug(f"Retrieved Documents: {retrieved_documents.get_text()}")
    
    return context

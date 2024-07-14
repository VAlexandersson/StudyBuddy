from logging import Logger

from src.tasks import Task
from src.models.data_models import Context, RetrievedDocuments

class RetrieveDocumentsTask(Task):
  def run(self, context: Context, logger: Logger) -> Context:

    documents = self.document_retriever.get_collection_documents( 
      context.query.text,
      col_name="nutrition_science",
      top_k=10
    )

    retrieved_documents = RetrievedDocuments(documents=documents)
    
    context.retrieved_documents = retrieved_documents
    logger.debug(f"Retrieved Documents: {retrieved_documents.get_text()}")
    
    return context

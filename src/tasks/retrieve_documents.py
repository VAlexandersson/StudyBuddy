from src.tasks import Task
from src.utils.logging_utils import logger

from src.models.context import Context
from src.models.document import RetrievedDocuments

class RetrieveDocumentsTask(Task):
  def run(self, context: Context) -> Context:

    documents = self.document_retriever.get_collection_documents( 
      context.query.text,
      col_name="nutrition_science",
      top_k=5
    )

    retrieved_documents = RetrievedDocuments(documents=documents)

    context.retrieved_documents = retrieved_documents
    logger.debug(f"Retrieved Documents: {retrieved_documents.get_text()}")
    return context

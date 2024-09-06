from src.tasks import Task
from src.models.context import Context
from src.interfaces.services.text_generation import TextGenerationService
from typing import Dict, Any
from src.tasks.tools.query_focused_summary import query_focused_summary

class TransformRetrievedDocumentsTask(Task):
  def __init__(self, name: str, services: Dict[str, Any]):
      super().__init__(name, services)
      self.text_generation_service: TextGenerationService = services['text_generation']


  async def run(self, context: Context) -> Context:

      for doc in context.retrieved_documents.documents:
        summary = await query_focused_summary(context.query.text, doc.document, self.text_generation_service)
        doc.transformed_document = summary
        
      print([{'id': doc.id, 'document': doc.transformed_document} for doc in context.retrieved_documents.documents])

      return context

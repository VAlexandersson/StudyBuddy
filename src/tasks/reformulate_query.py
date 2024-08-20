from src.tasks import Task
from src.models.context import Context
from src.interfaces.services.text_generation import TextGenerationService
from src.interfaces.services.document_retrieval import DocumentRetrievalService
from src.models.document import DocumentObject
from typing import Dict, Any, List
import json
from src.tasks.tools.binary_grade import binary_grade
from src.tasks.tools.binary_grade_document_relevance import binary_grade_document_relevance
from src.tasks.tools.query_focused_summary import query_focused_summary

class PostRetrievalTask(Task):
  def __init__(self, name: str, services: Dict[str, Any]):
      super().__init__(name, services)
      self.text_generation_service: TextGenerationService = services['text_generation']
      self.document_retrieval_service: DocumentRetrievalService = services['document_retrieval']


  async def run(self, context: Context) -> Context:
      print(f"QUERY: {context.query.text}")

      query = context.query.text

      indices_to_remove = []

      for i, doc in enumerate(context.retrieved_documents.documents):
        print(f"DOCUMENT: {doc.id}\n{doc.document}")

        grade = await binary_grade_document_relevance(doc, query, self.text_generation_service)

        print(f"GRADE: {grade}")

        if grade == 'no':
          print(f"Document {doc.id} is not relevant to the query.")
          indices_to_remove.append(i)

      for index in sorted(indices_to_remove, reverse=True):
        doc = context.retrieved_documents.documents.pop(index)
        context.retrieved_documents.filtered_documents.append(doc)
        print(f"Removed document at index {index} with id {doc.id}")

      for doc in context.retrieved_documents.documents:

        summary = await query_focused_summary(query, doc.document, self.text_generation_service)
        doc.transformed_document = summary
        
      print([{'id': doc.id, 'document': doc.transformed_document} for doc in context.retrieved_documents.documents])

      return context

from src.utils.logging_utils import logger
from src.tasks import Task
from src.tasks.tools.binary_grade import binary_grade
from src.tasks.utils.prompt_library import RELEVANCE_PROMPT
from src.models.context import Context 
from src.interfaces.services.text_generation import TextGenerationService
from typing import Dict, Any

class FilterDocumentsTask(Task):
  def __init__(self, name: str, services: Dict[str, Any]):
    super().__init__(name, services)
    self.text_generation_service: TextGenerationService = services['text_generation']

  async def run(self, context: Context) -> Context:
    user_prompt, system_prompt = RELEVANCE_PROMPT

    for doc in context.retrieved_documents.documents:
      grade = await binary_grade(user_prompt=user_prompt.format(doc, context.query.text), system_prompt=system_prompt, text_gen_service=self.text_generation_service)

      context.retrieved_documents.ignore.append(grade)
        
      print(f"Grade: {grade} - Doc ID: {doc.id} Text:\n{doc.document}")
    
    no_indices = [i for i, x in enumerate(context.retrieved_documents.ignore) if x == 'no']
    context.retrieved_documents.filtered_documents = [context.retrieved_documents.documents[i] for i in no_indices]
    context.retrieved_documents.documents = [doc for i, doc in enumerate(context.retrieved_documents.documents) if i not in no_indices]

    logger.debug(f"Filtered Documents: {context.retrieved_documents.filtered_documents}")

    return context
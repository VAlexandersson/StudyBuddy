from src.utils.logging_utils import logger
from src.tasks import Task
from src.tasks.tools.binary_grade import binary_grade
from src.models.context import Context 
from src.interfaces.services.text_generation import TextGenerationService
from typing import Dict, Any

class FilterDocumentsTask(Task):
  def __init__(self, name: str, services: Dict[str, Any]):
    super().__init__(name, services)
    self.text_generation_service: TextGenerationService = services['text_generation']

  async def run(self, context: Context) -> Context:
    #rel_user_prompt, rel_system_prompt = RELEVANCE_PROMPT

    system_prompt = """Assess if the retrieved document contains information directly relevant to answering the query: {context.query.text}.

Give a simple 'yes' or 'no' answer:
- 'yes' if the document contains specific information about the key aspect of the query
- 'no' if the document doesn't address these aspects or only mentions them tangentially

Respond with only this JSON format:
{"score": "yes"} or {"score": "no"}
"""
    user_prompt= "Retrieved document:\n{doc}"


    for doc in context.retrieved_documents.documents:
      grade = await binary_grade(
        user_prompt=user_prompt.format(doc=doc), #f"Retrieved document: \n\n {doc} \n\nQuery: {context.query.text}\n",
        system_prompt=system_prompt, 
        text_gen_service=self.text_generation_service
      )

      context.retrieved_documents.ignore.append(grade)
        
      print(f"Grade: {grade} - Doc ID: {doc.id}")
    
    no_indices = [i for i, x in enumerate(context.retrieved_documents.ignore) if x == 'no']
    context.retrieved_documents.filtered_documents = [context.retrieved_documents.documents[i] for i in no_indices]
    context.retrieved_documents.documents = [doc for i, doc in enumerate(context.retrieved_documents.documents) if i not in no_indices]

    logger.debug(f"Filtered Document IDs: {[doc.id for doc in context.retrieved_documents.filtered_documents]}")

    return context
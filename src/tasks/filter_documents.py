from src.utils.logging_utils import logger
from src.tasks import Task
from src.tasks.utils.binary_grade import binary_grade
from src.tasks.utils.prompt_library import RELEVANCE_PROMPT
from src.models.context import Context 
from src.service.manager import ServiceManager

class FilterDocumentsTask(Task):
  def run(self, context: Context) -> Context:
    user_prompt, system_prompt = RELEVANCE_PROMPT

    for doc in context.retrieved_documents.documents:
      text_gen_service = ServiceManager.get_service('text_generation')
      
      message = text_gen_service.generate_text(#self.inference_mediator.generate_response(
        user_prompt=user_prompt.format(doc, context.query.text), 
        system_prompt=system_prompt,
        temperature=0.1
      )
      grade = binary_grade(user_prompt=user_prompt.format(doc, context.query.text), 
        system_prompt=system_prompt)
        
      grade = binary_grade(message)
      context.retrieved_documents.ignore.append(grade)
      
      print(f"Grade: {grade} - Doc ID: {doc.id} Text:\n{doc.document}")
    
    no_indices = [i for i, x in enumerate(context.retrieved_documents.ignore) if x == 'no']
    context.retrieved_documents.filtered_documents = [context.retrieved_documents.documents[i] for i in no_indices]
    context.retrieved_documents.documents = [doc for i, doc in enumerate(context.retrieved_documents.documents) if i not in no_indices]

    logger.debug(f"Filtered Documents: {context.retrieved_documents.filtered_documents}")

    return context

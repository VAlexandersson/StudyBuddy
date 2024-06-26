from tasks.utils.binary_grade import binary_grade
from tasks.utils.prompt_library import RELEVANCE_PROMPT
from models.data_models import Context 
from tasks import Task
from logging import Logger
from service.manager import ServiceManager

class FilterDocumentsTask(Task):
  def run(self, context: Context, logger: Logger) -> Context:
    user_prompt, system_prompt = RELEVANCE_PROMPT

    for doc in context.retrieved_documents.documents:
      text_gen_service = ServiceManager.get_service('text_generation')
      
      message = text_gen_service.generate_text(#self.inference_mediator.generate_response(
        user_prompt=user_prompt.format(doc, context.query.text), 
        system_prompt=system_prompt,
        temperature=0.1
      )
        
      grade = binary_grade(message)
      context.retrieved_documents.ignore.append(grade)
      
      print(f"Grade: {grade} - Doc ID: {doc.id} Text:\n{doc.document}")
    
    no_indices = [i for i, x in enumerate(context.retrieved_documents.ignore) if x == 'no']
    context.retrieved_documents.filtered_documents = [context.retrieved_documents.documents[i] for i in no_indices]
    context.retrieved_documents.documents = [doc for i, doc in enumerate(context.retrieved_documents.documents) if i not in no_indices]

    logger.debug(f"Filtered Documents: {context.retrieved_documents.filtered_documents}")

    return context

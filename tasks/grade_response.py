from tasks.utils.prompt_library import HALLUCINATION_PROMPT
from models.data_models import Context
from service.manager import ServiceManager

from logging import Logger
from tasks import Task
from tasks.utils.binary_grade import binary_grade

class GradeResponseTask(Task):
  def run(self, context: Context, logger: Logger) -> Context:

    system_prompt, user_prompt = HALLUCINATION_PROMPT
    user_prompt.format(documents=context.retrieved_documents.get_text(), response=context.response.text)
    
    text_gen_service = ServiceManager.get_service('text_generation')


    message = text_gen_service.generate_text( #self.inference_mediator.generate_response(
      user_prompt=user_prompt,
      system_prompt=system_prompt,
      temperature=0.1
    )
    
    logger.debug(f"Response Grade: {message}")
    
    #TODO: FALLBACK ROUTE, If the response is graded as 'no', we will try again to provide a better response

    return context




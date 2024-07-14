from logging import Logger

from src.models.data_models import Context
from src.service.manager import ServiceManager
from src.tasks import Task
from src.tasks.utils.binary_grade import binary_grade
from src.tasks.utils.prompt_library import HALLUCINATION_PROMPT

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




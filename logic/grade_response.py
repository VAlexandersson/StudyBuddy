from utils.prompt_library import HALLUCINATION_PROMPT
from models.data_models import Context

from logging import Logger
from logic import Task
from logic.utils.binary_grade import binary_grade

class GradeResponseTask(Task):
  def run(self, context: Context, logger: Logger) -> Context:

    system_prompt, user_prompt = HALLUCINATION_PROMPT
    user_prompt.format(documents=context.retrieved_documents.get_text(), response=context.response.text)
    
    message = self.inference_mediator.generate_response(
      user_prompt=user_prompt, 
      system_prompt=system_prompt, 
      temperature=0.7
    )
    
    context.response.grade = binary_grade(message=message)
    logger.debug(f"Response Grade: {context.response.grade}")
    
    #TODO: FALLBACK ROUTE, If the response is graded as 'no', we will try again to provide a better response

    return context




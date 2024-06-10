from logic.prompt_library import HALLUCINATION_PROMPT
from models.data_models import PipelineContext

from logging import Logger
from logic.tasks.base_task import BaseTask
from logic.tasks.utils.binary_grade import binary_grade

class GradeResponseTask(BaseTask):
  def run(self, context: PipelineContext, logger: Logger) -> PipelineContext:

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




from src.utils.logging_utils import logger

from src.models.context import Context

from src.tasks import Task
from src.tasks.utils.binary_grade import binary_grade
from src.tasks.utils.prompt_library import HALLUCINATION_PROMPT

class GradeResponseTask(Task):
  def run(self, context: Context) -> Context:

    system_prompt, user_prompt = HALLUCINATION_PROMPT
    user_prompt.format(documents=context.retrieved_documents.get_text(), response=context.response.text)

    grade = binary_grade(user_prompt=user_prompt, system_prompt=system_prompt)
    
    logger.debug(f"Response Grade: {grade}")
    print(f"Response Grade: {grade}")
    #TODO: FALLBACK ROUTE, If the response is graded as 'no', we will try again to provide a better response

    return context

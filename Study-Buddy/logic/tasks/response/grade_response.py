# pipeline/tasks/grade_response.py
from configs.prompt_library import HALLUCINATION_PROMPT
from models.data_models import PipelineContext
from utils.binary_grade import binary_grade
from utils.format_prompt import format_prompt

from logic.tasks import Task
from logging import Logger

def grade_response(context: PipelineContext, logger: Logger) -> PipelineContext:
  system_prompt, user_prompt = HALLUCINATION_PROMPT
  user_prompt.format(documents=context.retrieved_documents.get_text(), response=context.response.text)
  prompt = format_prompt(user=user_prompt, system=system_prompt)
  context.response.grade = binary_grade(prompt).score
  logger.debug(f"Response Grade: {context.response.grade}")
  #TODO: FALLBACK ROUTE, If the response is graded as 'no', we will try again to provide a better response
  return context

GradeResponseTask = Task(
  name="GradeResponseTask",
  function=grade_response,
)
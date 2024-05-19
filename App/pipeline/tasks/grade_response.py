# pipeline/tasks/grade_response.py
from configs.prompt_library import HALLUCINATION_PROMPT
from pipeline.data_models import PipelineContext
from utils.binary_grade import binary_grade
from utils.format_prompt import format_prompt

from pipeline.tasks import Task
from logging import Logger


def grade_response(context: PipelineContext, logger: Logger) -> PipelineContext:
  system_prompt, user_prompt = HALLUCINATION_PROMPT
  user_prompt.format(documents=context.retrieved_documents.get_text(), response=context.response.text)
  prompt = format_prompt(user=user_prompt, system=system_prompt)
  context.response.grade = binary_grade(prompt).score
  logger.debug(f"Response Grade: {context.response.grade}")
  return context

GradeResponseTask = Task(
  name="GradeResponseTask",
  function=grade_response,
  next_tasks={
      None: "EndTask" # TODO if grade is bad. ask user if they want you to search the web 
  }
)
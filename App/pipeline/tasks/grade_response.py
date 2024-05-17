# pipeline/tasks/grade_response.py
from config.prompt_library import HALLUCINATION_PROMPT
from pipeline.data_models import PipelineContext
from utils.binary_grade import binary_grade
from utils.format_prompt import format_prompt

from pipeline.tasks import Task


def grade_response(context: PipelineContext) -> PipelineContext:
    system_prompt, user_prompt = HALLUCINATION_PROMPT
    user_prompt.format(documents=context.retrieved_documents.get_text(), response=context.response.text)
    prompt = format_prompt(user=user_prompt, system=system_prompt)
    context.response.grade = binary_grade(prompt).score
    return context

GradeResponseTask = Task(
  name="GradeResponseTask",
  function=grade_response,
  next_tasks={
      None: "EndTask" # TODO if grade is bad. ask user if they want you to search the web 
  }
)
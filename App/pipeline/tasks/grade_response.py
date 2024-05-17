from pipeline.tasks import Task
from pipeline.data_models import PipelineContext
from utils.binary_grade import binary_grade
from utils.format_prompt import format_prompt
from config.prompt_library import HALLUCINATION_PROMPT

# TODO Implement the logic
class GradeResponseTask(Task):
  def run(self, context: PipelineContext, prompt_type: str = HALLUCINATION_PROMPT) -> PipelineContext:
    system_prompt, user_prompt = HALLUCINATION_PROMPT
    user_prompt.format(documents=context.retrieved_documents.get_text(), response=context.response.text)

    prompt = format_prompt(user=user_prompt, system=system_prompt)

    context.response.grade = binary_grade(prompt)

    return context
from models.data_models import PipelineContext
from utils.binary_grade import binary_grade
from utils.format_prompt import format_prompt
from logging import Logger
from logic.tasks.base_task import BaseTask

MULTISTEP_QUERY_PROMPT = (
  "You are a multistep query classifier. Your goal is to determine if a given query requires multiple steps to answer or can be answered in a single step. Provide a binary 'yes' or 'no' score to indicate whether the query is a multistep query. Return the binary score as a JSON with a single key 'score' and no additional explanation.",
  "Here is the query: {query}"
)

class ClassifyMultistepQueryTask(BaseTask):
  def run(self, context: PipelineContext, logger: Logger) -> PipelineContext:
    system_prompt, user_prompt = MULTISTEP_QUERY_PROMPT
    user_prompt = user_prompt.format(query=context.query.text)
    prompt = format_prompt(user=user_prompt, system=system_prompt)
    context.query.is_multistep = binary_grade(prompt).score
    logger.debug(f"\n\tIs Multistep Query: {context.query.is_multistep}\n")
    return context
from src.utils.logging_utils import logger
from src.models.context import Context
from src.tasks import Task
from src.tasks.utils.binary_grade import binary_grade
from src.service.manager import ServiceManager

MULTISTEP_QUERY_PROMPT = (
  "You are a multistep query classifier. Your goal is to determine if a given query requires multiple steps to answer or can be answered in a single step. Provide a binary 'yes' or 'no' score to indicate whether the query is a multistep query. Return the binary score as a JSON with a single key 'score' and no additional explanation.",
  "Here is the query: {query}"
)

class ClassifyMultistepQueryTask(Task):
  def run(self, context: Context) -> Context:
    system_prompt, user_prompt = MULTISTEP_QUERY_PROMPT
    user_prompt = user_prompt.format(query=context.query.text)

    text_gen_service = ServiceManager.get_service('text_generation')
    message = text_gen_service.generate_text(#self.inference_mediator.generate_response(
      user_prompt=user_prompt,
      system_prompt=system_prompt,
      temperature=0.1
    )
    
    context.query.is_multistep = binary_grade(message)
    logger.debug(f"\n\tIs Multistep Query: {context.query.is_multistep}\n")
    return context



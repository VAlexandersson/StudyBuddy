from src.utils.logging_utils import logger
from src.tasks import Task
from src.models.context import Context
from src.interfaces.services.text_generation import TextGenerationService
from typing import Dict, Any

REFORMULATE_QUERY_PROMPT = (
  "You are a query reformulator. Your goal is to take a query and reformulate it into a clear, step-by-step format. Break down the query into simple, sequential steps that can be easily understood and processed. Each step should be numbered and end with a newline. Never answer with anything else than with the numbered steps.",
  "Here is the query: {query}"
)


class ReformulateQueryTask(Task):
  def __init__(self, name: str, services: Dict[str, Any]):
    super().__init__(name, services)
    self.text_generation_service: TextGenerationService = services['text_generation']

  async def run(self, context: Context):
    logger.debug(f"Raw Query: {context.query.text}")

    system_prompt, user_prompt = REFORMULATE_QUERY_PROMPT
    user_prompt = user_prompt.format(query=context.query.text)
    
    reformulated_query = self.text_generation_service.generate_text( 
      user_prompt=user_prompt,
      system_prompt=system_prompt,
      temperature=0.1,
    )

    context.query.text = reformulated_query
    logger.debug(f"Reformulated Query: {context.query.text}")
    logger.debug(f"Query History: {context.query.query_history}")

    return context
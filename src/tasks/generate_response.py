from src.utils.logging_utils import logger
from src.models.context import Context
from src.models.response import Response
from src.tasks import Task
from src.tasks.utils.prompt_library import STANDARD_PROMPT
from src.interfaces.services.text_generation import TextGenerationService
from typing import Dict, Any

class GenerateResponseTask(Task):
  def __init__(self, name: str, services: Dict[str, Any]):
    super().__init__(name, services)
    self.text_generation_service: TextGenerationService = services['text_generation']

  def run(self, context: Context) -> Context:
    print("\n")
    logger.debug(f"\n\tQuery:\n{context.query.text}\n\tLabel:\n{context.query.label}")

    if context.query.label not in ["question", "command"]:
      system_prompt = "You are Study Buddy. An assistant for students to use in their studies."
      user_prompt = context.query.text
    else:
      context.routing_key = "grade"

      logger.info(f"\n\tRetrieved Documents:\n {context.retrieved_documents.get_text()}\n")
      system_prompt = STANDARD_PROMPT["system"]
      user_prompt = STANDARD_PROMPT["user"]
      user_prompt = user_prompt.format(
        query=context.query.text, 
        retrieved_context=context.retrieved_documents.get_text()
      )
    
    context.response = Response(
      text=self.text_generation_service.generate_text(
        user_prompt=user_prompt,
        system_prompt=system_prompt,
        temperature=0.7
      )
    )
    return context
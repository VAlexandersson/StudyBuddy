from src.utils.logging_utils import logger
from src.service.manager import ServiceManager
from src.models.context import Context
from src.models.response import Response
from src.tasks import Task
from src.tasks.utils.prompt_library import STANDARD_PROMPT

# TODO: Break out format prompt into a separate task
class GenerateResponseTask(Task):
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
      
    text_gen_service = ServiceManager.get_service('text_generation')
    context.response = Response(
      text=text_gen_service.generate_text( #self.inference_mediator.generate_response(
        user_prompt=user_prompt,
        system_prompt=system_prompt,
        temperature=0.7
      )
    )
    return context

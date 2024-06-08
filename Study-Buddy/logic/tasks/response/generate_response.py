from logic.prompt_library import STANDARD_PROMPT
from models.data_models import PipelineContext, Response
#from language_models.text_generation import LLM
#from utils.format_prompt import format_prompt

from logging import Logger
from logic.tasks.base_task import BaseTask

# TODO: Break out format prompt into a separate task
class GenerateResponseTask(BaseTask):
  def run(self, context: PipelineContext, logger: Logger) -> PipelineContext:
 #   llm = LLM() 
    print("\n")
    logger.debug(f"\n\tQuery:\n{context.query.text}\n\tLabel:\n{context.query.label}")

    if context.query.label not in ["question", "command"]:
      system_prompt = "Be nice."
      user_prompt = context.query.text
      #context.response = Response(
       # text=self.inference_mediator.generate_response(  #llm.inference(format_prompt(
        #  context.query.text, 
      #))
    else:
      logger.info(f"\n\tRetrieved Documents:\n {context.retrieved_documents.get_text()}\n")
      system_prompt = STANDARD_PROMPT["system"]
      user_prompt = STANDARD_PROMPT["user"]
      user_prompt = user_prompt.format(
        query=context.query.text, 
        retrieved_context=context.retrieved_documents.get_text()
      )

     # context.response = Response(text=llm.inference(format_prompt(user=user_prompt, system=system_prompt)))

    context.response = Response(
      text=self.inference_mediator.generate_response(  #llm.inference(format_prompt(
        user_prompt=user_prompt,
        system_prompt=system_prompt,
        temperature=0.7
      )
    )
    return context

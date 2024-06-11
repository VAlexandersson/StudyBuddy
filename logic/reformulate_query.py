from models.data_models import PipelineContext
from logging import Logger
from logic import Task


REFORMULATE_QUERY_PROMPT = (
  "You are a query reformulator. Your goal is to take a query and reformulate it into a clear, step-by-step format. Break down the query into simple, sequential steps that can be easily understood and processed. Each step should be numbered and end with a newline. Never answer with anything else than with the numbered steps.",
  "Here is the query: {query}"
)


class ReformulateQueryTask(Task):
  def run(self, context: PipelineContext, logger: Logger):
    logger.debug(f"Raw Query: {context.query.text}")

    system_prompt, user_prompt = REFORMULATE_QUERY_PROMPT
    user_prompt = user_prompt.format(query=context.query.text)

 #   llm = LLM()
    reformulated_query = self.inference_mediator.generate_response( #llm.generate_response(
      user_prompt=user_prompt,
      system_prompt=system_prompt,
      temperature=0.1,
    )

    context.query.text = reformulated_query
    logger.debug(f"Reformulated Query: {context.query.text}")
    logger.debug(f"Query History: {context.query.query_history}")

    return context
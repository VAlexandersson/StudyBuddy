from models.data_models import Context
from logging import Logger
from logic import Task

class DecomposeQueryTask(Task):
  def run(self, context: Context, logger: Logger):
    decomposed_query = self.inference_mediator.generate_response(
        user_prompt=context.query.text,
        system_prompt="You are a query decomposer. Your goal is to take a query and decompose it into one to many parts depending on how complicated the query is. Your response should only concist of the decomposed parts as a list in json format.",
        temperature=0.1,
    )
    context.query.decomposed_parts = decomposed_query.split('\n')

    logger.debug(f"Decomposed Query: {context.query.decomposed_parts}")

    return context

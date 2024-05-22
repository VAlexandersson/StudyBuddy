from models.data_models import PipelineContext
from language_models.text_generation import LLM
from logging import Logger
from logic.tasks.base_task import BaseTask

class DecomposeQueryTask(BaseTask):
  def run(self, context: PipelineContext, logger: Logger):
    llm = LLM()
    decomposed_query = llm.generate_response(
        user=context.query.text,
        system="You are a query demcomposer. Your goal is to take a query and decompose it into one to many parts depending on how complicated the query is. Your response should only concist of the decomposed parts as a list in json format.",
        temperature=0.3,
    )
    context.query.decomposed_parts = decomposed_query.split('\n')

    logger.debug(f"Decomposed Query: {context.query.decomposed_parts}")

    return context

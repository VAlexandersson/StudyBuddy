# pipeline/tasks/decompose_query.py
from pipeline.data_models import PipelineContext
from models.text_generation import LLM
from pipeline.tasks import Task
from logging import Logger

def decompose_query(context: PipelineContext, logger: Logger) -> PipelineContext:
  llm = LLM()  
  decomposed_query = llm.generate_response(
      user=context.query.text, 
      system="You are a query demcomposer. Your goal is to take a query and decompose it into on to many parts depending on how complicated the query is. Your response should only concist of the decomposed parts as a list in json format."
  )
  context.query.decomposed_parts = decomposed_query.split('\n')
  
  logger.debug(f"Decomposed Query: {context.query.decomposed_parts}")

  return context

DecomposeQueryTask = Task(
  name="DecomposeQueryTask",
  function=decompose_query,
  next_tasks={
      None: "RetrieveDocumentsTask"
  }
) 
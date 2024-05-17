# pipeline/tasks/decompose_query.py
from pipeline.data_models import PipelineContext
from models.text_generation import LLM

from pipeline.tasks import Task

def decompose_query(context: PipelineContext) -> PipelineContext:
  print("Decomposing context...")
  llm = LLM()  
  decomposed_query = llm.generate_response(
      user=context.query.text, 
      system="Decompose the context into its constituent parts."
  )
  context.query.decomposed_parts = decomposed_query.split('\n') 
  return context

DecomposeQueryTask = Task(
  name="DecomposeQueryTask",
  function=decompose_query,
  next_tasks={
      None: "RetrieveDocumentsTask"
  }
) 
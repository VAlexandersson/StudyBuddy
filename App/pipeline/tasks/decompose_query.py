# App/pipeline/tasks/decompose_query.py
from pipeline.tasks import Task
from models.text_generation import LLM
from pipeline.data_models import PipelineContext

class DecomposeQueryTask(Task):
  def __init__(self):
    self.llm = LLM()

  def run(self, context: PipelineContext) -> PipelineContext:

    print("Decomposing context...")
    decomposed_query = self.llm.generate_response(
        user=context.query.text, 
        system="Decompose the context into its constituent parts."
    )

    context.query.decomposed_parts = decomposed_query.split('\n') # Assuming parts are separated by newlines
    return context
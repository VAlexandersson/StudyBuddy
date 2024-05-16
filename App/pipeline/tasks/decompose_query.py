# App/pipeline/tasks/decompose_query.py
from pipeline.tasks import Task
from models.text_generation import LLM
from pipeline.data_models import Query

class DecomposeQueryTask(Task):
  def __init__(self):
    self.llm = LLM()

  def run(self, query: Query) -> Query:

    print("Decomposing query...")
    decomposed_query = self.llm.generate_response(
        user= query.text, 
        system="Decompose the query into its constituent parts."
    )

    query.decomposed_parts = decomposed_query.split('\n') # Assuming parts are separated by newlines
    return query
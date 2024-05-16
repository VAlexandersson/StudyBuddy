# App/pipeline/tasks/preprocess_query.py
from pipeline.tasks import Task
from utils.text_preprocessing import preprocess_text
from pipeline.data_models import Query

class PreprocessQueryTask(Task):
  def run(self, query: str) -> Query:
    print("Preprocessing query...")
    preprocessed_text = preprocess_text(query)
    return Query(text=preprocessed_text)
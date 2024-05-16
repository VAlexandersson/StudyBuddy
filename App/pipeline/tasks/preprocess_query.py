# App/pipeline/tasks/preprocess_query.py
from pipeline.tasks import Task
from utils.text_preprocessing import preprocess_text
from pipeline.data_models import PipelineContext

class PreprocessQueryTask(Task):
  def run(self, context: PipelineContext) -> PipelineContext:
    print("Preprocessing query...")
    preprocessed_text = preprocess_text(context.query.text)
    return PipelineContext(text=preprocessed_text)
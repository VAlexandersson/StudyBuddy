from utils.text_preprocessing import preprocess_text
from pipeline.data_models import PipelineContext
from pipeline.tasks import Task
from logging import Logger

def preprocess_query(context: PipelineContext, logger: Logger) -> PipelineContext:
  logger.debug(f"Raw Query: {context.query.text}")
  # Assuming preprocess_text function is defined elsewhere
  preprocessed_text = preprocess_text(context.query.text)
  context.query.text = preprocessed_text
  logger.debug(f"Processed Query: {context.query.text}")
  return context

PreprocessQueryTask = Task(
  name="PreprocessQueryTask",
  function=preprocess_query,
  next_tasks={
    None: "ClassifyQueryTask"  # 'None' acts as a default key for any routing_key
  }
)
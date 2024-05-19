from utils.text_preprocessing import preprocess_text
from models.data_models import PipelineContext
from logic.tasks import Task
from logging import Logger

def preprocess_query(context: PipelineContext, logger: Logger) -> PipelineContext:
  logger.debug(f"Raw Query: {context.query.text}")


  preprocessed_text = preprocess_text(context.query.text)
  context.query.text = preprocessed_text
  logger.debug(f"Processed Query: {context.query.text}")
  return context

PreprocessQueryTask = Task(
  name="PreprocessQueryTask",
  function=preprocess_query,
)
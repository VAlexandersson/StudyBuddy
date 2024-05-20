from utils.text_preprocessing import preprocess_text
from models.data_models import PipelineContext
from logging import Logger
from logic.tasks.base_task import BaseTask

class PreprocessQueryTask(BaseTask):
  def run(self, context: PipelineContext, logger: Logger):
    logger.debug(f"Raw Query: {context.query.text}")

    preprocessed_text = preprocess_text(context.query.text)

    context.query.text = preprocessed_text
    logger.debug(f"Processed Query: {context.query.text}")
    return context

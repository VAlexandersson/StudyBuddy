from models.data_models import PipelineContext
from logging import Logger
from logic.tasks.base_task import BaseTask
import string
import re

class PreprocessQueryTask(BaseTask):
  
  
  def run(self, context: PipelineContext, logger: Logger):
    logger.debug(f"Raw Query: {context.query.text}")

    text = context.query.text.lower()
    text = text.translate(str.maketrans("", "", string.punctuation))
    text = re.sub(r"\s+", " ", text).strip()
    context.query.text = text
    
    logger.debug(f"Processed Query: {context.query.text}")
    return context



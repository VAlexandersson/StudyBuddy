from models.data_models import PipelineContext
from logging import Logger
from logic import Task
import string
import re

class PreprocessQueryTask(Task):
  
  
  def run(self, context: PipelineContext, logger: Logger):
    logger.debug(f"Raw Query: {context.query.text}")

    text = context.query.text.lower()
    text = text.translate(str.maketrans("", "", string.punctuation))
    text = re.sub(r"\s+", " ", text).strip()
    context.query.text = text
    
    logger.debug(f"Processed Query: {context.query.text}")
    return context



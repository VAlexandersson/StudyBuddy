import re
import string
from src.utils.logging_utils import logger
from src.models.context import Context
from src.tasks import Task

class PreprocessQueryTask(Task):
  
  
  def run(self, context: Context):
    logger.debug(f"Raw Query: {context.query.text}")

    text = context.query.text.lower()
    text = text.translate(str.maketrans("", "", string.punctuation))
    text = re.sub(r"\s+", " ", text).strip()
    context.query.text = text
    
    logger.debug(f"Processed Query: {context.query.text}")
    return context



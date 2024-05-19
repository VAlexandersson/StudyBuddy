import json
import logging
import logging.config

logger = logging.getLogger(__name__)

def configure_logger(name):
  logger = logging.getLogger(name)
  logger.setLevel(logging.INFO)
  # Create console handler with a higher log level
  ch = logging.StreamHandler()
  ch.setLevel(logging.INFO)
  # Create formatter and add it to the handlers
  formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
  ch.setFormatter(formatter)
  # Add the handlers to the logger
  logger.addHandler(ch)
  return logger

def setup_logging():
  config_file = "logging/logging_config.json"
  with open(config_file, "r") as f:
    config = json.load(f)
  logging.config.dictConfig(config)
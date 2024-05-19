import json
import logging
import logging.config

logger = logging.getLogger(__name__)

def configure_logger(name):
  logger = logging.getLogger(name)
  logger.setLevel(logging.INFO)

  ch = logging.StreamHandler()
  ch.setLevel(logging.INFO)

  formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
  ch.setFormatter(formatter)

  logger.addHandler(ch)
  return logger

def setup_logging():
  config_file = "logging/logging_config.json"
  with open(config_file, "r") as f:
    config = json.load(f)
  logging.config.dictConfig(config)
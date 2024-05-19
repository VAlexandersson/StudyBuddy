# App/pipeline/tasks/__init__.py
from logging import Logger
from typing import Callable, Optional
from models.data_models import PipelineContext
from configs.routing_config import ROUTING_CONFIG

Runnable = Callable[[PipelineContext], PipelineContext] # type alias

class Task:
  def __init__(self, name: str, function: Runnable):
    self.name = name
    self.function = function
    self.routing_config = ROUTING_CONFIG.get(self.name, {})

  def run(self, context: PipelineContext, logger: Logger) -> PipelineContext:
    """
    Executes the task's function and updates the pipeline context.
    """
    logger.info(f"Running task: {self.name}")
    return self.function(context, logger)

  def get_next_task(self, routing_key: str) -> Optional[str]:
    """
    Determines the next task to run based on the routing key.
    """
    return self.routing_config.get(routing_key)
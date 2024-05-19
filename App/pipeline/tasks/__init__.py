# App/pipeline/tasks/__init__.py
from logging import Logger
from typing import Callable, Optional, Dict
from pipeline.data_models import PipelineContext

Runnable = Callable[[PipelineContext], PipelineContext]

class Task:
  def __init__(self, name: str, function: Runnable, next_tasks: Optional[Dict[str, str]] = None):
    self.name = name
    self.function = function
    self.next_tasks = next_tasks if next_tasks else {}

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
    return self.next_tasks.get(routing_key)
from typing import List
from logging import Logger
from pipeline.tasks import Task
from pipeline.data_models import Query, PipelineContext

class StudyBuddy:
  def __init__(self, tasks: List[Task]):
    self.tasks = {task.name: task for task in tasks}

  def run(self, query: Query, logger: Logger) -> PipelineContext:
    context = PipelineContext(query=query)
    current_task = self.tasks["PreprocessQueryTask"] # starting task

    while current_task:
      context = current_task.run(context, logger)
      logger.info(f"Routing Key: {context.routing_key}") 
      next_task_name = current_task.get_next_task(context.routing_key)
      logger.info(f"Next Task: {next_task_name}")
      current_task = self.tasks.get(next_task_name)
      logger.info(f"Current Task: {current_task}")
      context.routing_key = None # reset routing key

    return context
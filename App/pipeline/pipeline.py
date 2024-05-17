from typing import List, Optional
from pipeline.tasks import Task


# TODO: Eliminate the distinction between tasks and pipelines by combining them into a single class.
class Pipeline:
  """Manages the execution of tasks in a pipeline."""
  def __init__(self, tasks: List[Task]):
    self.tasks = tasks

  def get_task(self, task_name: str) -> Optional[Task]:
    for task in self.tasks:
      if type(task).__name__ == task_name:
        return task
    return None
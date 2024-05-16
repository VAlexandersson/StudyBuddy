from typing import List, Optional
from pipeline.tasks import Task

class Pipeline:
  """Manages the execution of tasks in a pipeline."""
  def __init__(self, tasks: List[Task]):
    self.tasks = tasks

  def get_task(self, task_name: str) -> Optional[Task]:
    for task in self.tasks:
      if type(task).__name__ == task_name:
        return task
    return None
  

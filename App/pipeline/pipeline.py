# App/pipeline/pipeline.py
from typing import List, Dict, Any
from pipeline.tasks import Task
from pipeline.router import Router

class Pipeline:
  """Manages the execution of tasks in a pipeline."""
  def __init__(self, tasks: List[Task]):
    self.router = Router(tasks)

  def run(self, query: str) -> Dict[str, Any]:
    data = query
    while True: 
      task = self.router.get_next_task(data)
      if task is None:
        break
      print(f"Running task: {type(task).__name__}")
      data = task.run(data)
    return data
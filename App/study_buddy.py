from router import Router
from typing import List, Dict, Any
from pipeline.tasks import Task
from pipeline.pipeline import Pipeline
from pipeline.data_models import Query, PipelineContext

class StudyBuddy:
  def __init__(self, tasks: List[Task]):
    self.pipeline = Pipeline(tasks)
    self.router = Router(self.pipeline)

  def run(self, query: Query) -> Dict[str, Any]:
    context = PipelineContext(query=query)
    while True:
      task_name = self.router.get_next_task(context)
      if task_name is None or task_name == "EndTask":
        break
      task = self.pipeline.get_task(task_name)
      if task is None:
        raise ValueError(f"Task not found: {task_name}")
      print(f"Running task: {task_name}")
      context = task.run(context)
    return context.response
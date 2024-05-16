# App.pipeline.router.py
from typing import Dict, Any, List
from pipeline.tasks import Task
from pipeline.data_models import Query, RetrievedDocuments, ReRankedDocuments, GradedDocuments, Response 
from utils.load_yaml import load_yaml_config

data_type_to_task = {
  Query: "ClassifyQueryTask",
  RetrievedDocuments: "RetrieveDocumentsTask",
  ReRankedDocuments: "ReRankingTask",
  GradedDocuments: "DocumentRemoval",
  Response: "GenerateResponseTask"
}

class Router:
  """Routes the pipeline execution based on task results."""
  def __init__(self, tasks: List[Task]):
    self.tasks = tasks
    self.current_task_index = 0
    self.routing_rules = load_yaml_config("routing_rules.yaml")["routing_rules"]

    print(f"Routing rules:\n{self.routing_rules}")
  def get_routing_key(self, last_task_name, data):
    if last_task_name == "ClassifyQueryTask":
      return data.classification
    return last_task_name

  def get_next_task(self, data: Query | RetrievedDocuments | ReRankedDocuments | GradedDocuments | Response ) -> Task:
    """
    Determines the next task to execute based on the pipeline data.
    Uses routing rules to determine the next task in the sequence.
    """
    print(f"Routing data: {type(data).__name__}")

    last_task_name = data_type_to_task.get(type(data), "PreprocessQueryTask")
    self.current_task_index += 1
    print(f"Last task name: {last_task_name}")
    
    routing_key = self.get_routing_key(last_task_name, data)
    print(f"Routing key: {routing_key}")

    next_task_name = self.routing_rules.get(routing_key)
    print(f"Next task name: {next_task_name}")
 
    if next_task_name is None:
      return None

    next_task = next(task for task in self.tasks if type(task).__name__ == next_task_name)
    return next_task
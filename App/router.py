from typing import Optional
from pipeline.pipeline import Pipeline
from pipeline.data_models import Query, RetrievedDocuments, ReRankedDocuments, GradedDocuments, Response, PipelineContext
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
  def __init__(self, pipeline: Pipeline):
    self.pipeline = pipeline
    self.current_task_index = 0
    self.routing_rules = load_yaml_config("routing_rules.yaml")["routing_rules"]

    print(f"Routing rules:\n{self.routing_rules}")
  def get_routing_key(self, last_task_name, data):
    if last_task_name == "ClassifyQueryTask":
      return data.classification
    return last_task_name

  def get_next_task(self, context: PipelineContext) -> Optional[str]:
    """
    Determines the next task to execute based on the pipeline data.
    Uses routing rules to determine the next task in the sequence.
    """
    print(f"Routing data: {type(context.query).__name__}")

    last_task_name = context.last_task 
    self.current_task_index += 1
    print(f"Last task name: {last_task_name}")
    
    routing_key = self.get_routing_key(last_task_name, context.query)
    print(f"Routing key: {routing_key}")

    next_task_name = self.routing_rules.get(routing_key)
    print(f"Next task name: {next_task_name}")

    context.last_task = next_task_name

    return next_task_name
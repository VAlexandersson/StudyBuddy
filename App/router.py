from typing import Optional, Dict, Any
from pipeline.pipeline import Pipeline
from pipeline.data_models import PipelineContext

class Router:
  """Routes the pipeline execution based on task results."""
  def __init__(self, pipeline: Pipeline):
    self.pipeline = pipeline
    self.routing_rules: Dict[str, Any] = {
      "PreprocessQueryTask": {
          None: "ClassifyQueryTask" # 'None' acts as a default key for any routing_key
      },
      "ClassifyQueryTask": {
          "course_query": "DecomposeQueryTask",
          "general_query": "GenerateResponseTask",
      },
      "DecomposeQueryTask": {
          None: "RetrieveDocumentsTask",
      },
      "RetrieveDocumentsTask": {
          None: "ReRankingTask"
      },
      "ReRankingTask": {
          None: "DocumentRemoval"
      },
      "DocumentRemoval": {
          None: "GenerateResponseTask"
      },
      "GenerateResponseTask": {
          None: "GradeResponseTask"
      },
      "GradeResponseTask": {
          None: "EndTask"
      }
    } 

    print(f"Routing rules:\n{self.routing_rules}")
  def get_routing_key(self, context: PipelineContext):
    if context.last_task == "ClassifyQueryTask":
      return context.routing_key
    return context.last_task

  def get_next_task(self, context: PipelineContext) -> Optional[str]:
    """
    Determines the next task to execute based on the pipeline data.
    Uses routing rules to determine the next task in the sequence.
    """

    context.routing_key = self.get_routing_key(context)
    print(f"Routing key: {context.routing_key}")
    
    print(f"Keys: {context.routing_key}")
    
    next_task_name = self.routing_rules.get(context.last_task, {}).get(context.routing_key)
    if next_task_name is None:
      next_task_name = self.routing_rules.get(context.last_task, {}).get(None)
    print(f"Next task name: {next_task_name}")

    context.last_task = next_task_name

    return next_task_name
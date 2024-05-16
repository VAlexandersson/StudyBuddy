# App/pipeline/router.py
from typing import Dict, Any, List
from pipeline.tasks import Task
from pipeline.data_models import Query, RetrievedDocuments, ReRankedDocuments, GradedDocuments, Response 


class Router:
  """Routes the pipeline execution based on task results."""

  def __init__(self, tasks: List[Task]):
    self.tasks = tasks
    self.current_task_index = -1
    self.routing_rules = {
      "PreprocessQueryTask": "ClassifyQueryTask",
      ("ClassifyQueryTask", "course_query"): "DecomposeQueryTask",
      ("ClassifyQueryTask", "general_query"): "RetrieveDocumentsTask",
      "DecomposeQueryTask": "RetrieveDocumentsTask",
      "RetrieveDocumentsTask": "ReRankingTask",
      "ReRankingTask": "DocumentRemoval",
      "DocumentRemoval": "GenerateResponseTask",
      "GenerateResponseTask": "GradeResponseTask",
      "GradeResponseTask": None,  # Termination
    }

  def get_next_task(self, data: Query | RetrievedDocuments | ReRankedDocuments | GradedDocuments | Response ) -> Task:
    """
    Determines the next task to execute based on the pipeline data.
    Uses routing rules to determine the next task in the sequence.
    """

    print(f"Routing data: {type(data).__name__}")

    self.current_task_index += 1
    
    if self.current_task_index == 0:
      last_task_name = "PreprocessQueryTask"
    elif isinstance(data, Query):
      last_task_name = "ClassifyQueryTask"
    elif isinstance(data, RetrievedDocuments):
      last_task_name = "RetrieveDocumentsTask"
    elif isinstance(data, ReRankedDocuments):
      last_task_name = "ReRankingTask"
    elif isinstance(data, GradedDocuments):
      last_task_name = "DocumentRemoval"
    elif isinstance(data, Response):
      last_task_name = "GenerateResponseTask"
    else:
      raise ValueError("Invalid data type for routing")
    
    print(f": {last_task_name}")
    
    if last_task_name == "ClassifyQueryTask":
      routing_key = (last_task_name, data.classification)
    else:
      routing_key = last_task_name
      
    next_task_name = self.routing_rules.get(routing_key)

    if next_task_name is None:
      return None

    next_task = next(task for task in self.tasks if type(task).__name__ == next_task_name)
    return next_task
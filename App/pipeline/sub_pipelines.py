# App/pipeline/sub_pipelines.py
from typing import List
from pipeline.tasks import Task 
from pipeline.data_models import Query, GradedDocuments 

class RetrievalPipeline:
    """Manages the document retrieval and processing sub-pipeline."""
    def __init__(self, tasks: List[Task]):
        self.tasks = tasks 

    def run(self, query: Query) -> GradedDocuments:
        data = query
        for task in self.tasks:
            data = task.run(data)
        return data

class QueryProcessingPipeline:
  """Manages the query preprocessing and classification sub-pipeline."""
  def __init__(self, tasks: List[Task]):
    self.tasks = tasks

  def run(self, query: str) -> Query:
  
    data = query
    for task in self.tasks:
        data = task.run(data)
    return data
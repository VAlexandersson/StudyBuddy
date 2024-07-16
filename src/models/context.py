from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from src.models.query import Query
from src.models.document import RetrievedDocuments
from src.models.response import Response

class Context(BaseModel):
  query: Query = Query()
  retrieved_documents: Optional[RetrievedDocuments] = RetrievedDocuments()
  response: Optional[Response] = Response()
  last_task: Optional[str] = "PreprocessQueryTask"
  routing_key: Optional[str] = "default"
  response_type: Optional[str] = None

  task_history: List[Dict[str, Any]] = []

  def add_to_history(self, task_name: str, output: Optional[Dict[str, Any]] = None):
    self.task_history.append({"task": task_name, "output": output})
    
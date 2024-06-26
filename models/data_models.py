from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class DocumentObject(BaseModel):
  id: str
  document: str
  embeddings: List = None
  metadatas: Dict

class Query(BaseModel):
  text: str = ""
  reformulated_query: Optional[str] = ""
  query_history: Optional[List[str]] = []
  decomposed_parts: Optional[List[str]] = []

  label: Optional[str] = "" 
  is_multistep: Optional[bool] = False
  
  embeddings: List = []
  @property
  def text(self):
    return self.text
  
  @text.setter
  def text(self, value):
    if self._text:
      self.query_history.append(self._text)
    self._text = value

class RetrievedDocuments(BaseModel):
  documents: List[DocumentObject] = []
  original_order: Optional[List[str]] = []
  ignore: Optional[List[str]] = []
  filtered_documents: Optional[List[DocumentObject]] = []

  def get_text(self):
    return "\n-  ".join([doc.document for doc in self.documents])
  
  def add_document(self, document: DocumentObject):
    self.documents.append(document)

  def remove_document(self, document_id: str):
    self.documents = [doc for doc in self.documents if doc.id != document_id]

class Response(BaseModel):
  text: str = ""
  grade: Optional[str] = None

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
    
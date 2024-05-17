# App/pipeline/data_models.py
from pydantic import BaseModel
from typing import List, Optional, Dict


class DocumentObject(BaseModel):
    id: str
    document: str
    embeddings: List = None
    metadatas: Dict

    
class Query(BaseModel):
    text: str = ""
    classification: Optional[str] = None 
    decomposed_parts: Optional[List[str]] = []


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


class PipelineContext(BaseModel):
    query: Query = Query()
    retrieved_documents: Optional[RetrievedDocuments] = RetrievedDocuments()
    response: Optional[Response] = Response()
    last_task: Optional[str] = "PreprocessQueryTask"
    routing_key: Optional[str] = None
    
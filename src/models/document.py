from typing import List, Dict, Optional
from pydantic import BaseModel

class DocumentObject(BaseModel):
  id: str
  document: str
  embeddings: List = None
  metadatas: Dict

  refined_document: Optional[str] = None


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
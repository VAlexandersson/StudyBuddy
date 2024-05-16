# App/pipeline/data_models.py
from pydantic import BaseModel
from typing import List, Optional, Dict

class DocumentObject(BaseModel):
    id: str
    document: str
    embeddings: List = None
    metadatas: Dict
    
class Query(BaseModel):
    text: str
    classification: Optional[str] = None 
    decomposed_parts: Optional[List[str]] = None

class RetrievedDocuments(BaseModel):
    documents: List[DocumentObject]
    original_order: Optional[List[str]] = None
    ignore: Optional[List[str]] = None
    filtered_documents: Optional[List[DocumentObject]] = None
    
class Response(BaseModel):
    text: str
    grade: Optional[str] = None

class PipelineContext(BaseModel):
    query: Query
    retrieved_documents: Optional[RetrievedDocuments] = None
    response: Optional[Response] = None
    last_task: Optional[str] = "PreprocessQueryTask"
    routing_key: Optional[str] = None
    
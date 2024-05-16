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
    query: Query 
    documents: List[DocumentObject]
    original_order: List[str]
    unfiltered_documents: List[DocumentObject]
    
class Response(BaseModel):
    query: Query
    text: str
    grade: Optional[str] = None

class PipelineContext(BaseModel):
    query: Query
    retrieved_documents: Optional[RetrievedDocuments] = None
    response: Optional[Response] = None
    last_task: Optional[str] = "PreprocessQueryTask"




class ReRankedDocuments(BaseModel):
    query: Query
    documents: List[DocumentObject]

class GradedDocuments(BaseModel):
    query: Query
    documents: List[DocumentObject]
    grades: List[str]
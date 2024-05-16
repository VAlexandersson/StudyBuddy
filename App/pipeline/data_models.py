# App/pipeline/data_models.py
from pydantic import BaseModel
from typing import List, Optional, Dict

class Query(BaseModel):
    text: str
    classification: Optional[str] = None 
    decomposed_parts: Optional[List[str]] = None 

class DocumentObject(BaseModel):
    id: str
    document: str
    embeddings: List = None
    metadatas: Dict
    
class RetrievedDocuments(BaseModel):
    query: Query 
    documents: List[DocumentObject]
    
class ReRankedDocuments(BaseModel):
    query: Query
    documents: List[DocumentObject]

class GradedDocuments(BaseModel):
    query: Query
    documents: List[DocumentObject]
    grades: List[str] # "yes" or "no"

class Response(BaseModel):
    query: Query
    text: str
    grade: Optional[str] = None
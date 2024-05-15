from pydantic import BaseModel
from typing import List, Dict
# Object {
#   ids: text
#   documents text
#   metadatas {
#     Chapter, 
#     ParentChapter, 
#     Keywords, 
#     OrderID, 
#     Page, 
#     Summary, 
#     Type, 
#     course, 
#     type
#   }
# }
#
class DocumentObject(BaseModel):
    id: str
    document: str
    embeddings: List = None
    metadatas: Dict
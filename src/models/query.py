from typing import List, Optional
from pydantic import BaseModel

class Query(BaseModel):
  text: str = None
  reformulated_query: Optional[str] = None
  query_history: Optional[List[str]] = []
  decomposed_parts: Optional[List[str]] = []

  label: Optional[str] = None
  is_multistep: Optional[bool] = False
  
  embeddings: List = []
  @property
  def text(self):
    return self.text
  
  @text.setter
  def text(self, value):
    if self.text:
      self.query_history.append(self.text)
    self.text = value
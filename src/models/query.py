from typing import List, Optional
from pydantic import BaseModel

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
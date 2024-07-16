from pydantic import BaseModel
from typing import Optional

class Response(BaseModel):
  text: str = ""
  grade: Optional[str] = None
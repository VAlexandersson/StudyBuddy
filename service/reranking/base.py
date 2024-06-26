from abc import ABC, abstractmethod
from typing import List

class ReRankingService(ABC):
  @abstractmethod
  def rerank(self, query: str, documents: List[str]) -> List[float]:
    pass

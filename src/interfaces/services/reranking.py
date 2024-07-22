from abc import ABC, abstractmethod
from typing import List

class RerankingService(ABC):
  @abstractmethod
  def rerank(self, query_doc_pair: List) -> List[float]:
    pass
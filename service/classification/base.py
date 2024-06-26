from abc import ABC, abstractmethod
from typing import List, Dict, Any

class ClassificationService(ABC):
  @abstractmethod
  def classify(self, query: str, labels: List[str], hypothesis_template: str) -> Dict[str, Any]:
    pass

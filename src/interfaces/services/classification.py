from abc import ABC, abstractmethod
from typing import List, Dict, Any

class ClassificationService(ABC):
    @abstractmethod
    async def classify(self, query: str, labels: List[str], hypothesis_template: str, multi_label: bool = True) -> Dict[str, Any]:
        pass
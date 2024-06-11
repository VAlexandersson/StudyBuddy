from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple

class EmbeddingModelInterface(ABC):
    @abstractmethod
    def encode(self, query: str) -> List:
        pass

    @abstractmethod
    def encode_batch(self, documents: List[str], batch_size: int, convert_to_tensor: bool, show_progress_bar: bool) -> List:
        pass

class TextGeneratorInterface(ABC):
    @abstractmethod
    def generate_response(self, query: str, context: str, temperature: float) -> str:
        pass

class ZeroShotClassifierInterface(ABC):
    @abstractmethod
    def classify(self, query: str, labels: List[str], hypothesis_template: str, multi_label: bool) -> Dict[str, Any]:
        pass

class ReRankerModelInterface(ABC):
    @abstractmethod
    def predict(self, sentences: List[Tuple[str, str]]) -> List[float]:
        pass


class InferenceMediator(ABC):
  
    """     
    @abstractmethod
    def encode_query(self, query: str) -> List:
        pass

    @abstractmethod
    def encode_documents(self, documents: List[str], batch_size: int, convert_to_tensor: bool, show_progress_bar: bool) -> List:
        pass
    """
    @abstractmethod
    def generate_response(self, user_prompt: str, system_prompt: str, temperature: float) -> str:
        pass

    @abstractmethod
    def classify_query(self, query: str, labels: List[str], hypothesis_template: str, multi_label: bool) -> Dict[str, Any]:
        pass

    @abstractmethod
    def rerank_documents(self, query_doc_pair: List) -> List[float]:
        pass


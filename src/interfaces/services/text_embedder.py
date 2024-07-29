from abc import ABC, abstractmethod
from typing import List

class TextEmbeddingService(ABC):
    @abstractmethod
    async def encode(self, query: str) -> List:
        pass

    @abstractmethod
    async def encode_batch(self, documents: List[str], batch_size: int, convert_to_tensor: bool, show_progress_bar: bool) -> List:
        pass
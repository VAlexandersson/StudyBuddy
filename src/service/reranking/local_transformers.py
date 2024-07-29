from src.interfaces.services.reranking import RerankingService
from typing import List
from sentence_transformers import CrossEncoder
import asyncio

class LocalTransformerReranking(RerankingService):
    def __init__(self, model_id: str) -> None:
        self.cross_encoder = CrossEncoder(model_id)
        print(f"Loaded Cross-Encoder model: {model_id}")

    async def rerank(self, query_doc_pair: List) -> List[float]:
        loop = asyncio.get_event_loop()
        scores = await loop.run_in_executor(None, self.cross_encoder.predict, query_doc_pair)
        return scores
from src.interfaces.services.reranking import RerankingService
from typing import List
from sentence_transformers import CrossEncoder

class LocalTransformerReranking(RerankingService):
  def __init__(self, model_id: str) -> None:
    self.cross_encoder = CrossEncoder(model_id)
    print(f"Loaded Cross-Encoder model: {model_id}")

  def rerank(self, query_doc_pair: List):
    return self.cross_encoder.predict(query_doc_pair)



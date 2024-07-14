from .base import ReRankingService
from src.adapter.reranker.cross_encoder import DocReRanker
from typing import List

class TransformerRerankingService(ReRankingService):
  def __init__(self):
    self.reranker = DocReRanker(model_id = 'cross-encoder/ms-marco-MiniLM-L-12-v2')

  def rerank(self, query_doc_pair: List) -> List[float]:
    return self.reranker.predict(query_doc_pair)

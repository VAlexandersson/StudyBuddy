from src.utils.logging_utils import logger
from src.tasks import Task
from src.models.context import Context
from src.interfaces.services.reranking import RerankingService
from typing import Dict, Any

class ReRankingTask(Task):
  def __init__(self, name: str, services: Dict[str, Any]):
    super().__init__(name, services)
    self.rerank_service: RerankingService = services['reranking']

  async def run(self, context: Context, top_k: int = 5) -> Context:
    query = context.query.text
    documents = context.retrieved_documents.documents

    query_doc_pairs = [(query, doc.document) for doc in documents]
    print(f"Query Doc Pairs:\n{len(query_doc_pairs)}")
    
    scores = await self.rerank_service.rerank(query_doc_pairs)
    context.retrieved_documents.original_order = [doc.id for doc in documents]

    combined = list(zip(scores, documents))
    combined.sort(key=lambda x: x[0], reverse=True)

    top_documents = [item[1] for item in combined[:top_k]]
    filtered_documents = [item[1] for item in combined[top_k:]]
    
    context.retrieved_documents.documents = top_documents
    context.retrieved_documents.filtered_documents = filtered_documents

    logger.debug(f"ReRanked Order: {[doc.id for doc in top_documents]}")
    logger.debug(f"Filtered Documents: {[doc.id for doc in filtered_documents]}")
    
    return context
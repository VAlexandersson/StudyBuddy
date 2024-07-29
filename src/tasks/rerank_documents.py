from src.utils.logging_utils import logger
from src.tasks import Task
from src.models.context import Context
from src.interfaces.services.reranking import RerankingService
from typing import Dict, Any

class ReRankingTask(Task):
    def __init__(self, name: str, services: Dict[str, Any]):
        super().__init__(name, services)
        self.rerank_service: RerankingService = services['reranking']

    async def run(self, context: Context) -> Context:
        query = context.query.text
        documents = context.retrieved_documents.documents

        query_doc_pairs = [(query, doc.document) for doc in documents]
        print(f"Query Doc Pairs:\n{query_doc_pairs}")
        
        scores = await self.rerank_service.rerank(query_doc_pairs)
        context.retrieved_documents.original_order = [doc.id for doc in documents]

        combined = list(zip(scores, documents))
        combined.sort(key=lambda x: x[0], reverse=True)
        
        documents = [item[1] for item in combined]
        context.retrieved_documents.documents = documents

        logger.debug(f"ReRanked Documents: {documents}")
        
        return context
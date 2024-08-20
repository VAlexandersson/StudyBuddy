from src.models.context import Context
from src.models.query import Query
from pydantic import BaseModel
from src.models.document import DocumentObject
from src.task_manager import TaskManager
from typing import List

from src.interfaces.services.document_retrieval import DocumentRetrievalService
from src.interfaces.services.text_generation import TextGenerationService
from src.interfaces.services.classification import ClassificationService
from src.interfaces.services.reranking import RerankingService

from src.utils.config_manager import ConfigManager

class Response(BaseModel):
    query: str
    context_objects: List[DocumentObject]
    answer: str

class RAGSystem:
    def __init__(
        self,
        config: ConfigManager,
        text_generation_service: TextGenerationService,
        classification_service: ClassificationService,
        reranking_service: RerankingService,
        document_retrieval_service: DocumentRetrievalService
    ):
        self.config = config
        
        services = {
          "text_generation_service": text_generation_service,
          "classification_service": classification_service,
          "reranking_service": reranking_service,
          "document_retrieval_service": document_retrieval_service
        }
        
        self.task_manager = TaskManager(config._config, services)
        
    async def process_query(self, query: str, eval: bool = False) -> Response | Context:
        context = Context(query=Query(text=query))
        current_task = "PreprocessQueryTask"

        while current_task != "EndTask":
          context = await self.task_manager.execute_task(current_task, context)
          current_task = self.task_manager.get_next_task(current_task, context.routing_key)
          context.routing_key = "default"

        if eval:
          return context
        
        response = Response(
            query=context.query.text,
            context_objects=context.retrieved_documents.documents,
            answer=context.response.text
        )

        return response

from src.models.context import Context
from src.models.query import Query
from pydantic import BaseModel
from src.models.document import DocumentObject
from src.task_manager import TaskManager
from typing import List
import importlib

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
        
    def _initialize_tasks(self):
        task_config = self.config.get("TASKS", [])
        routing_config = self.config.get("ROUTING", {})
        task_instances = {}
        
        for task_info in task_config:
            task_name = task_info["name"]
            task_class_path = task_info["class"]
            required_services = task_info.get("services", [])

            module_path, class_name = task_class_path.rsplit(".", 1)
            module = importlib.import_module(module_path)
            task_class = getattr(module, class_name)

            service_instances = {}
            for service in required_services:
                service_attr = f"{service}_service"
                if not hasattr(self, service_attr):
                    raise AttributeError(f"Required service '{service}' not found for task '{task_name}'")
                service_instances[service] = getattr(self, service_attr)

            task_args = {
                "name": task_name,
                "services": service_instances
            }

            task_instance = task_class(**task_args)
            task_instance.routing_config = routing_config.get(task_name, {})
            task_instances[task_name] = task_instance

        return task_instances

    async def process_query(self, query: str) -> Response:
        context = Context(query=Query(text=query))
        current_task = "PreprocessQueryTask"

        while current_task != "EndTask":

          context = await self.task_manager.execute_task(current_task, context)
          current_task = self.task_manager.get_next_task(current_task, context.routing_key)

          
            #context = await self._run_task(current_task, context)
            #next_task_name = current_task.get_next_task(context.routing_key)
            #current_task = self.tasks.get(next_task_name)
          context.routing_key = "default"

        response = Response(
            query=context.query.text,
            context_objects=context.retrieved_documents.documents,
            answer=context.response.text
        )

        return response

    async def _run_task(self, task, context: Context) -> Context:
        try:
            return await task.run(context)
        except Exception as e:
            print(f"Error running task {task.name}: {str(e)}")
            return context

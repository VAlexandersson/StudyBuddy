from src.models.context import Context
from src.models.response import Response
from src.models.query import Query

import importlib
from src.service.manager import ServiceManager

from src.interfaces.knowledge_base import KnowledgeBase
from src.utils.config_manager import ConfigManager


class RAGSystem:
  def __init__(
    self, 
    knowledge_base: KnowledgeBase,
    config: ConfigManager, 
    service_manager: ServiceManager = None,
    ):

    self.knowledge_base = knowledge_base
    self.config = config
    self.service_manager = service_manager or ServiceManager.get_instance()

    self.tasks = self._initialize_tasks()
    
    
  def _initialize_tasks(self):
    task_config = self.config.get("TASKS", [])
    routing_config = self.config.get("ROUTING", {})
    task_instances = {}
    for task_info in task_config:
      task_name = task_info["name"]
      task_class_path = task_info["class"]
      module_path, class_name = task_class_path.rsplit(".", 1)
      module = importlib.import_module(module_path)
      task_class = getattr(module, class_name)
      
      task_instance = task_class(
        name=task_name, 
        retrieve_documents=self.knowledge_base
      )
      
      task_instance.routing_config = routing_config.get(task_name, {})
      task_instances[task_name] = task_instance
    return task_instances

  def process_query(self, query: str) -> Response:
    context = Context(query=Query(text=query))
    current_task = self.tasks["PreprocessQueryTask"]

    while current_task:
      
      context = current_task.run(context)
      next_task_name = current_task.get_next_task(context.routing_key)
      current_task = self.tasks.get(next_task_name)
      context.routing_key = "default"
      
    return context.response

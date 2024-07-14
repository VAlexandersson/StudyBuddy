import importlib
from logging import Logger
from src.config.config_manager import config_manager
from src.models.data_models import Context, Response

from src.interfaces.user_interface import UserInterface
from src.interfaces.knowledge_base import KnowledgeBaseManager

from src.service.manager import ServiceManager

class StudyBuddy:
  def __init__(
      self, 
      ui: UserInterface, 
      knowledge_base_manager: KnowledgeBaseManager, 
      logger: Logger
    ):

    ServiceManager.get_instance()

    self.ui = ui
    self.logger = logger
    self.knowledge_base_manager = knowledge_base_manager
    
    self.tasks = self._initialize_tasks()
    
  def _initialize_tasks(self):
    task_config = config_manager.get("TASKS", [])
    routing_config = config_manager.get("ROUTING", {})
    task_instances = {}
    for task_info in task_config:
      task_name = task_info["name"]
      task_class_path = task_info["class"]
      module_path, class_name = task_class_path.rsplit(".", 1)
      module = importlib.import_module(module_path)
      task_class = getattr(module, class_name)
      
      task_instance = task_class(
        name=task_name, 
        retrieve_documents=self.knowledge_base_manager
      )
      
      task_instance.routing_config = routing_config.get(task_name, {})
      task_instances[task_name] = task_instance
    return task_instances

  def run(self) -> Context:
    while True:
      query = self.ui.get_query()
      if not query.text.strip():
        continue
      if query.text.lower() in ["exit", "bye", "quit", "adios"]:
        self.ui.post_response(Response(text="Goodbye!"))
        break

      context = Context(query=query)
      current_task = self.tasks["PreprocessQueryTask"]

      while current_task:
        self.logger.info(f"Current Task: {current_task}")
        
        context = current_task.run(context, self.logger)
        self.logger.info(f"Routing Key: {context.routing_key}")

        next_task_name = current_task.get_next_task(context.routing_key)
        self.logger.info(f"Next Task: {next_task_name}")

        current_task = self.tasks.get(next_task_name)

        context.routing_key = "default"
        
      self.ui.post_response(context.response)
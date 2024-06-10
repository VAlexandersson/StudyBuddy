import importlib
from logging import Logger
from config.config_manager import config_manager
from view.base_ui import BaseUI
from models.data_models import PipelineContext, Response
from language_models.inference_mediator_interface import InferenceMediatorInterface
from knowledge_base.knowledge_base_interface import KnowledgeBaseInterface

class StudyBuddy:
  def __init__(
      self, 
      ui: BaseUI, 
      document_retriever: KnowledgeBaseInterface, 
      inference_mediator: InferenceMediatorInterface, 
      logger: Logger
    ):
       
    self.ui = ui
    self.logger = logger
    self.inference_mediator = inference_mediator
    self.document_retriever = document_retriever
    
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
        inference_mediator=self.inference_mediator,
        retrieve_documents=self.document_retriever
      )
      
      task_instance.routing_config = routing_config.get(task_name, {})
      task_instances[task_name] = task_instance
    return task_instances

  def run(self) -> PipelineContext:
    while True:
      query = self.ui.get_query()
      if not query.text.strip():
        continue
      if query.text.lower() in ["exit", "bye", "quit", "adios"]:
        self.ui.post_response(Response(text="Goodbye!"))
        break

      context = PipelineContext(query=query)
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
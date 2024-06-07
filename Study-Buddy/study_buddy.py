import importlib
from logging import Logger
from config_manager import config_manager
from view.study_buddy_ui import StudyBuddyUI
from models.data_models import PipelineContext, Response

class StudyBuddy:
  def __init__(self, ui: StudyBuddyUI):
    self.tasks = self._initialize_tasks()
    self.ui = ui
    print(self.tasks["PreprocessQueryTask"].routing_config)
    
  def _initialize_tasks(Self):
    task_config = config_manager.get("TASKS", [])
    routing_config = config_manager.get("ROUTING", {})
    task_instances = {}
    for task_info in task_config:
      task_name = task_info["name"]
      task_class_path = task_info["class"]
      module_path, class_name = task_class_path.rsplit(".", 1)
      module = importlib.import_module(module_path)
      task_class = getattr(module, class_name)
      task_instance = task_class(name=task_name)
      task_instance.routing_config = routing_config.get(task_name, {})
      task_instances[task_name] = task_instance
    return task_instances

  def run(self, logger: Logger) -> PipelineContext:
    while True:
      query = self.ui.get_user_query()
      if not query.text.strip():
        continue
      if query.text.lower() == "exit" or query.text.lower() == "bye":
        self.ui.display_response(Response(text="Goodbye!"))
        break

      context = PipelineContext(query=query)
      current_task = self.tasks["PreprocessQueryTask"]

      while current_task:
        logger.info(f"Current Task: {current_task}")
        # logger.info(f"Context: {context}")
        
        context = current_task.run(context, logger)
        logger.info(f"Routing Key: {context.routing_key}")

        next_task_name = current_task.get_next_task(context.routing_key)
        logger.info(f"Next Task: {next_task_name}")

        current_task = self.tasks.get(next_task_name)

        context.routing_key = "default"
        
      self.ui.display_response(context.response)
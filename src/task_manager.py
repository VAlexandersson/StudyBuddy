import importlib
from typing import Dict, Any
from src.models.context import Context
from src.tasks import Task

class TaskManager:
  def __init__(self, config: Dict[str, Any], services: Dict[str, Any]):
    self.tasks = self._initialize_tasks(config, services)
    self.routing_config = config.get("ROUTING", {})

  def _initialize_tasks(self, config: Dict[str, Any], services: Dict[str, Any]) -> Dict[str, Task]:
    task_config = config.get("TASKS", [])
    task_instances = {}

    for task_info in task_config:
      task_name = task_info["name"]
      task_class_path = task_info["class"]
      required_services = task_info.get("services", [])

      module_path, class_name = task_class_path.rsplit(".", 1)
      module = importlib.import_module(module_path)
      task_class = getattr(module, class_name)

      service_instances = {service: services[f"{service}_service"] for service in required_services}

      task_instance = task_class(name=task_name, services=service_instances)
      task_instances[task_name] = task_instance

    return task_instances
  
  def reload_tasks(self):
    """Reload and reinitialize tasks."""
    self.tasks = self._initialize_tasks(self.config, self.services)

  def get_task(self, task_name: str) -> Task:
    task = self.tasks.get(task_name)
    if not task:
      raise ValueError(f"Task {task_name} not found")
    return task

  async def execute_task(self, task_name: str, context: Context) -> Context:
    task = self.get_task(task_name)
    return await task.run(context)

  def get_next_task(self, current_task: str, routing_key: str) -> str:
    return self.routing_config.get(current_task, {}).get(routing_key, "EndTask")
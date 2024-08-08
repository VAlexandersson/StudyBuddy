from src.models.context import Context
from src.tasks import Task
from src.interfaces.services.classification import ClassificationService

from src.tasks.tools.classification_tool import classify_and_get_top_label

from typing import Dict, Any

HYPOTHESIS_TEMPLATE = "This prompt is a {}"
LABELS = ["question", "statement", "command", "greeting", "goodbye"]
ROUTES = ["question", "command"]

class ClassifyQueryTask(Task):
  def __init__(self, name: str, services: Dict[str, Any]):
    super().__init__(name, services)
    self.classification_service: ClassificationService = services['classification']

  async def run(self, context: Context) -> Context:

    label = classify_and_get_top_label(self.classification_service, context.query.text, LABELS, HYPOTHESIS_TEMPLATE)

    route = label if (label in ROUTES) else "default"
    
    print(f"Route: {route}")

    context.routing_key = route
    context.query.label = label
    context.response_type = label
    return context
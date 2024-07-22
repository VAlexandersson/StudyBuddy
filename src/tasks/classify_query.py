from src.utils.logging_utils import logger
from src.models.context import Context
from src.tasks import Task
from src.interfaces.services.classification import ClassificationService
from typing import Dict, Any

HYPOTHESIS_TEMPLATE = "This prompt is a {}"
LABELS = ["question", "statement", "command", "greeting", "goodbye"]
ROUTES = ["question", "command"]

class ClassifyQueryTask(Task):
  def __init__(self, name: str, services: Dict[str, Any]):
    super().__init__(name, services)
    self.classification_service: ClassificationService = services['classification']

  def run(self, context: Context) -> Context:
    logger.info(f"Classifying Query: {context.query.text}")

    output = self.classification_service.classify(context.query.text, LABELS, HYPOTHESIS_TEMPLATE)
    
    logger.debug(f"Label scores: {output}")
    
    labels_scores = zip(output["labels"], output["scores"])
    label, score = max(labels_scores, key=lambda pair: pair[1])
    
    route = label if (label in ROUTES) else "default"
    
    print(f"Route: {route}")

    context.routing_key = route
    context.query.label = label
    context.response_type = label
    return context
from src.utils.logging_utils import logger
from src.models.context import Context
from src.tasks import Task
from src.service.manager import ServiceManager

HYPOTHESIS_TEMPLATE = "This prompt is a {}"
LABELS = ["question", "statement", "command", "greeting", "goodbye"]
ROUTES = ["question", "command"]


class ClassifyQueryTask(Task):
  def run(self, context: Context) -> Context:
    
    logger.info(f"Classifying Query: {context.query.text}")


    classification_service = ServiceManager.get_service('classification')

    
    
    output = classification_service.classify(context.query.text, LABELS, HYPOTHESIS_TEMPLATE)
    
    logger.debug(f"Label scores: {output}")
    
    labels_scores = zip(output["labels"], output["scores"])
    label, score = max(labels_scores, key=lambda pair: pair[1])
    
    route = label if (label in ROUTES) else "default"
    
    print(f"Route: {route}")

    context.routing_key = route
    context.query.label = label
    context.response_type = label
    return context

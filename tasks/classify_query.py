from models.data_models import Context
from logging import Logger
from config.classifier_config import LABELS, HYPOTHESIS_TEMPLATE 
from tasks import Task
from service.manager import ServiceManager

class ClassifyQueryTask(Task):
  def run(self, context: Context, logger: Logger) -> Context:
    
    logger.info(f"Classifying Query: {context.query.text}")


    classification_service = ServiceManager.get_service('classification')

    
    
    output = classification_service.classify(context.query.text, LABELS, HYPOTHESIS_TEMPLATE)
    
    logger.debug(f"Label scores: {output}")
    
    labels_scores = zip(output["labels"], output["scores"])
    label, score = max(labels_scores, key=lambda pair: pair[1])
    
    route = label if (label in ["question", "command"]) else "default"
    
    print(f"Route: {route}")

    context.routing_key = route
    context.query.label = label
    context.response_type = label
    return context

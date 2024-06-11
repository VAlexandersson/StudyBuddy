from models.data_models import Context
from logging import Logger
from config.classifier_config import LABELS, HYPOTHESIS_TEMPLATE 
from tasks import Task

class ClassifyQueryTask(Task):
  def run(self, context: Context, logger: Logger) -> Context:
    
    logger.info(f"Classifying Query: {context.query.text}")
    output = self.inference_mediator.classify_query(context.query.text, LABELS, HYPOTHESIS_TEMPLATE)
    logger.debug(f"Label scores: {output}")
    
    labels_scores = zip(output["labels"], output["scores"])
    label, score = max(labels_scores, key=lambda pair: pair[1])
    
    route = label if (label in ["question", "command"]) else "default"
    
    print(f"Route: {route}")

    context.routing_key = route
    context.query.label = label
    context.response_type = label
    return context

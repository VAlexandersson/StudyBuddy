from models.data_models import PipelineContext
#from language_models.zero_shot_classifier import ZeroShotClassifier
from logging import Logger
from config.classifier_config import LABELS, HYPOTHESIS_TEMPLATE 
from logic.tasks.base_task import BaseTask

class ClassifyQueryTask(BaseTask):
  def run(self, context: PipelineContext, logger: Logger) -> PipelineContext:
    
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

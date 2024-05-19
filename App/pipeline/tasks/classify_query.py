from pipeline.data_models import PipelineContext
from models.zero_shot_classifier import ZeroShotClassifier
from pipeline.tasks import Task
from logging import Logger
from configs.classifier_config import LABELS, HYPOTHESIS_TEMPLATE 

# TODO Dont feed labels only, feed labels that are mapped to the routing keys
def classify_query(context: PipelineContext, logger: Logger) -> PipelineContext:
  classifier = ZeroShotClassifier()
  logger.info(f"Classifying Query: {context.query.text}")
  output = classifier.classify(
    context.query.text,
    LABELS,
    HYPOTHESIS_TEMPLATE
  )
  logger.debug(f"Label scores: {output}")
  labels_scores = zip(output["labels"], output["scores"])
  label, score = max(labels_scores, key=lambda pair: pair[1])
  route = "rag" if label == "question" else "general"
  
  context.routing_key = route
  context.query.label = label
  context.response_type = label

  return context
  

ClassifyQueryTask = Task(
  name="ClassifyQueryTask",
  function=classify_query,
  next_tasks={
    "rag": "EmbedQueryTask", #"DecomposeQueryTask",
    "general": "GenerateResponseTask",
  }
)
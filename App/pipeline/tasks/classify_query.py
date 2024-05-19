
from pipeline.data_models import PipelineContext
from models.zero_shot_classifier import ZeroShotClassifier
from pipeline.tasks import Task
from logging import Logger

# TODO Dont feed labels only, feed labels that are mapped to the routing keys
def classify_query(context: PipelineContext, logger: Logger) -> PipelineContext:
  classifier = ZeroShotClassifier()
  logger.info(f"Classifying Query: {context.query.text}")
  output = classifier.classify(
    context.query.text,
    labels=["question", "statement", "greeting", "goodbye"]
  )
  logger.debug(f"Label scores: {output}")
  labels_scores = zip(output["labels"], output["scores"])
  label, score = max(labels_scores, key=lambda pair: pair[1])
  print(f"\n\nLabel: {label}\n\n")
  route = "rag" if label == "question" else "general"
  
  context.routing_key = route
  context.query.label = label
  context.response_type = label

  return context
  

ClassifyQueryTask = Task(
  name="ClassifyQueryTask",
  function=classify_query,
  next_tasks={
      "rag": "RetrieveDocumentsTask", #"DecomposeQueryTask",
      "general": "GenerateResponseTask",
  }
)
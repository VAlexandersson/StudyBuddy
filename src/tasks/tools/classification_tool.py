from src.interfaces.services.classification import ClassificationService
from typing import List

async def classify_and_get_top_label(classification_service: ClassificationService, query: str, labels: List[str], hypothesis_template: str) -> str | None:

  output = await classification_service.classify(
    query=query,
    labels=labels,
    hypothesis_template=hypothesis_template
  )
  
  labels_scores = zip(output["labels"], output["scores"])
  label, score = max(labels_scores, key=lambda pair: pair[1])

  return label
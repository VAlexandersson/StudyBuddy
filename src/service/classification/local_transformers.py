from src.interfaces.services.classification import ClassificationService

from typing import Any, Dict, List, cast
from transformers import pipeline

class LocalTransformerClassification(ClassificationService):
  def __init__(self, model_id: str) -> None:
    # https://arxiv.org/abs/1907.12461
    self.zero_shot_classifier = pipeline(
      "zero-shot-classification", 
      model=model_id
    )

  def classify(self, query, labels: List[str], hypothesis_template: str, multi_label=True):
    """
    Classifies the given query using zero-shot classification.

    Args:
      query (str): The input query to classify.
      labels (List[str]): The list of labels to classify the query against.
      hypothesis_template (str): The template for generating hypotheses.
      multi_label (bool, optional): Whether to allow multiple labels for classification. Defaults to True.

    Returns:
      Dict[str, Any]: The classification output.

    """
    output = cast(Dict[str, Any], self.zero_shot_classifier(
      query,
      labels,
      hypothesis_template=hypothesis_template,
      multi_label=multi_label,
    ))
    return output

from .base import ClassificationService
from src.adapter.classifier.zero_shot_classifier import ZeroShotClassifier
from typing import Any, Dict, List

class TransformerClassificationService(ClassificationService):
  def __init__(self):
    self.zero_shot_classifier = ZeroShotClassifier(model_id= "MoritzLaurer/deberta-v3-large-zeroshot-v2.0")

  def classify(self, query: str, labels: List[str], hypothesis_template: str, multi_label: bool = True) -> Dict[str, Any]:
    return self.zero_shot_classifier.classify(query, labels, hypothesis_template, multi_label)





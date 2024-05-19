from transformers import pipeline
from typing import Dict, Any, cast
from utils.singleton import Singleton

@Singleton
class ZeroShotClassifier:
  def __init__(self, model_id:str = "MoritzLaurer/deberta-v3-large-zeroshot-v2.0"):
    # https://arxiv.org/abs/1907.12461
    self.zeroshot_classifier = pipeline(
      "zero-shot-classification", 
      model=model_id
    )
    print(f"Loaded Zero-Shot Classifier model: {model_id}")

  def classify(self, query, labels, hypothesis_template, multi_label=True):
    output = cast(Dict[str, Any], self.zeroshot_classifier(
      query,
      labels,
      hypothesis_template=hypothesis_template,
      multi_label=multi_label,
    ))
    return output
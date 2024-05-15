from typing import List
from utils.singleton import Singleton
from sentence_transformers import CrossEncoder

@Singleton
class ReRankerModel:
  def __init__(self, model_id:str = 'cross-encoder/ms-marco-MiniLM-L-12-v2') -> None:
    self.cross_encoder = CrossEncoder(model_id)
    print(f"Loaded Cross-Encoder model: {model_id}")

  def predict(self, sentences):
    return self.cross_encoder.predict(sentences)
from utils.singleton import Singleton
from sentence_transformers import CrossEncoder

@Singleton
class DocReRanker:
  def __init__(self, model_id: str) -> None:
    self.cross_encoder = CrossEncoder(model_id)
    print(f"Loaded Cross-Encoder model: {model_id}")

  def predict(self, sentences):
    return self.cross_encoder.predict(sentences)
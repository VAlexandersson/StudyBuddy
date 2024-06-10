from language_models.inference_mediator import InferenceMediator
from language_models.transformers.zero_shot_classifier import ZeroShotClassifier
from language_models.transformers.text_generator import TextGenerator
from language_models.transformers.cross_encoder import DocReRanker
from typing import List, Dict, Any
 
class InferenceMediator(InferenceMediator):
  def __init__(self):
    self.text_generator = TextGenerator(model_id = "meta-llama/Meta-Llama-3-8B-Instruct", device = "cuda", attn_implementation = "sdpa")
    self.zero_shot_classifier = ZeroShotClassifier(model_id= "MoritzLaurer/deberta-v3-large-zeroshot-v2.0")
    self.reranker_model = DocReRanker(model_id = 'cross-encoder/ms-marco-MiniLM-L-12-v2')
    
  """ 
  def encode_query(self, query: str) -> List:
    return self.embedding_model.encode(query)

  def encode_documents(self, documents: List[str], batch_size: int, convert_to_tensor: bool, show_progress_bar: bool) -> List:
    return self.embedding_model.encode_batch(documents, batch_size, convert_to_tensor, show_progress_bar)
  """
  def generate_response(self, user_prompt:str, system_prompt:str, temperature: float = 0.7) -> str:
    return self.text_generator.generate_response(user_prompt, system_prompt, temperature)

  def classify_query(self, query: str, labels: List[str], hypothesis_template: str, multi_label: bool = True) -> Dict[str, Any]:
    return self.zero_shot_classifier.classify(query, labels, hypothesis_template, multi_label)

  def rerank_documents(self, query_doc_pair: List) -> List[float]:
    return self.reranker_model.predict(query_doc_pair)
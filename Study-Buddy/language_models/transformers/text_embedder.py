from utils.singleton import Singleton
from config_manager import config_manager
from sentence_transformers import SentenceTransformer
from language_models.base_models import EmbeddingModelInterface
@Singleton
class TextEmbedder(EmbeddingModelInterface):
  def __init__(self):
    self.model_id = config_manager.get("MODEL_IDS", {}).get("embedding_model")
    if not self.model_id:
      raise ValueError("Embedding model not found in config file")
    
    self.embedding_model = SentenceTransformer(self.model_id)
    print(f"Loaded Sentence Transformer model: {self.model_id}")
    
  def encode(self, query):
    query_embeddings = self.embedding_model.encode(
      query,
      convert_to_tensor=True
    ).tolist()

    return query_embeddings

  def encode_batch(self, query, batch_size: int=32, convert_to_tensor: bool=True, show_progress_bar: bool=True):
    return self.embedding_model.encode(
      query, 
      batch_size=batch_size, 
      convert_to_tensor=convert_to_tensor, 
      show_progress_bar=show_progress_bar
    )

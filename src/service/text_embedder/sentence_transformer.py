from sentence_transformers import SentenceTransformer
from src.interfaces.services.text_embedder import TextEmbeddingService

class TextEmbedder(TextEmbeddingService):
  def __init__(self, model_id: str = "BAAI/bge-m3"): #"sentence-transformers/all-mpnet-base-v2"):
    
    self.embedding_model = SentenceTransformer(model_id)
    print(f"Loaded Sentence Transformer model: {model_id}")
    
  def encode(self, query):# -> List | Any:
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

import logging
from sentence_transformers import SentenceTransformer
from src.interfaces.services.text_embedder import TextEmbeddingService
import asyncio

logger = logging.getLogger(__name__)

class TextEmbedding(TextEmbeddingService):
    def __init__(self, model_id: str = "BAAI/bge-m3"):
        self.embedding_model = SentenceTransformer(model_id)
        logger.info(f"Loaded Sentence Transformer model: {model_id}")
    
    async def encode(self, query):
        logger.debug(f"Encoding query: {query}")
        loop = asyncio.get_event_loop()
        try:
            query_embeddings = await loop.run_in_executor(
                None,
                self._encode_sync,
                query
            )
            logger.debug(f"Query encoded successfully. Shape: {query_embeddings.shape}")
            return query_embeddings.tolist()
        except Exception as e:
            logger.error(f"Error encoding query: {e}")
            raise

    def _encode_sync(self, query):
        return self.embedding_model.encode(query, convert_to_tensor=True)

    async def encode_batch(self, query, batch_size: int=32, convert_to_tensor: bool=True, show_progress_bar: bool=True):
        logger.debug(f"Encoding batch. Batch size: {batch_size}")
        loop = asyncio.get_event_loop()
        try:
            embeddings = await loop.run_in_executor(
                None,
                self._encode_batch_sync,
                query,
                batch_size,
                convert_to_tensor,
                show_progress_bar
            )
            logger.debug(f"Batch encoded successfully. Shape: {embeddings.shape}")
            return embeddings
        except Exception as e:
            logger.error(f"Error encoding batch: {e}")
            raise

    def _encode_batch_sync(self, query, batch_size, convert_to_tensor, show_progress_bar):
        return self.embedding_model.encode(
            query,
            batch_size=batch_size,
            convert_to_tensor=convert_to_tensor,
            show_progress_bar=show_progress_bar
        )
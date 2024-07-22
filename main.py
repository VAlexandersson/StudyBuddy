from src.rag_system import RAGSystem

from src.adapter.chromadb import ChromaDB
from src.utils.config_manager import ConfigManager
from src.view.command_line_ui import CommandLineUI

from src.service.text_embedder.sentence_transformer import TextEmbedding
from src.service.text_generation.local_transformers import LocalTransformerTextGeneration
from src.service.classification.local_transformers import LocalTransformerClassification
from src.service.reranking.local_transformers import LocalTransformerReranking
from src.service.document_retrieval.chromadb import ChromaDocumentRetrievalService

def main():

  config = ConfigManager()

  text_embedding_service = TextEmbedding(model_id = "BAAI/bge-m3")
  chromadb = ChromaDB(embedding_service=text_embedding_service)

  text_generation_service = LocalTransformerTextGeneration(
    model_id = "meta-llama/Meta-Llama-3-8B-Instruct", 
    device = "cuda", 
    attn_implementation = "sdpa"
  )
  
  classification_service = LocalTransformerClassification(
    model_id = "MoritzLaurer/deberta-v3-large-zeroshot-v2.0"
  )
  
  reranking_service = LocalTransformerReranking(
    model_id = 'BAAI/bge-reranker-v2-m3'
  )

  document_retrieval_service = ChromaDocumentRetrievalService(
    client=chromadb.get_client(),
    embedding_service=chromadb.get_embedding_service()
  )
  
  rag_system = RAGSystem(
    config=config,
    text_generation_service=text_generation_service,
    classification_service=classification_service,
    reranking_service=reranking_service,
    document_retrieval_service=document_retrieval_service
  )
  
  study_buddy = CommandLineUI(rag_system)
  study_buddy.run()

if __name__ == "__main__":
  main()
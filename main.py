import asyncio
import yaml
import importlib
import logging

from src.rag_system import RAGSystem
from src.adapter.chromadb import ChromaDB
from src.utils.config_manager import ConfigManager
from src.view.command_line_ui import CommandLineUI

from archive.all_eval.evaluation import RAGEvaluator

logging.basicConfig(level=logging.DEBUG)


with open("config/service_config.yaml", "r") as file:
  config = yaml.safe_load(file)


def get_class(module_path, class_name):
  module = importlib.import_module(module_path)
  return getattr(module, class_name)


async def init_services():
  text_embedding_service_class = get_class(config['text_embedding_service']['path'], config['text_embedding_service']['class'])
  text_embedding_service = text_embedding_service_class(model_id=config['text_embedding_service']['model_id'])
  
  chromadb = ChromaDB(embedding_service=text_embedding_service)
  
  text_generation_service_class = get_class(config['text_generation_service']['path'], config['text_generation_service']['class'])
  text_generation_service = text_generation_service_class(
    model_id=config['text_generation_service']['model_id'],
    device=config['text_generation_service']['device'],
    attn_implementation=config['text_generation_service']['attn_implementation']
  )
  
  classification_service_class = get_class(config['classification_service']['path'], config['classification_service']['class'])
  classification_service = classification_service_class(
    model_id=config['classification_service']['model_id']
  )
  
  reranking_service_class = get_class(config['reranking_service']['path'], config['reranking_service']['class'])
  reranking_service = reranking_service_class(
    model_id=config['reranking_service']['model_id']
  )
  
  document_retrieval_service_class = get_class(config['document_retrieval_service']['path'], config['document_retrieval_service']['class'])
  document_retrieval_service = document_retrieval_service_class(
    client=chromadb.get_client(),
    embedding_service=chromadb.get_embedding_service()
  )

  services = {
    "text_generation_service": text_generation_service,
    "classification_service": classification_service,
    "reranking_service": reranking_service,
    "document_retrieval_service": document_retrieval_service
  }
  
  return services

async def main(mode:str = '', conf:str = None):
    config = ConfigManager(env=conf or 'dev')
    services = await init_services()
    
    rag_system = RAGSystem(config=config, **services)

    if mode == 'eval':
      eval_buddy = RAGEvaluator(rag_system=rag_system)
      await eval_buddy.run()

    else:
      study_buddy = CommandLineUI(rag_system)
      await study_buddy.run()

if __name__ == "__main__":
    asyncio.run(main())
from src.rag_system import RAGSystem

from src.adapter.knowledge_base.chroma_db import ChromaDB
from src.utils.config_manager import ConfigManager
from src.view.command_line_ui import CommandLineUI

from src.utils.logging_utils import logger



def main():
  
  config = ConfigManager()
  knowledge_base = ChromaDB()
  
  logger.info("Initializing RAG System")  
  rag_system = RAGSystem(
    knowledge_base=knowledge_base,
    config=config,
  )
  
  study_buddy = CommandLineUI(rag_system)
  study_buddy.run()

if __name__ == "__main__":
  main()
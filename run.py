from study_buddy import StudyBuddy

from knowledge_base.chroma.chroma_db import ChromaDB
from view.command_line_ui import CommandLineUI
import logging

logging.basicConfig(
    level=logging.DEBUG, 
    format='%(asctime)s - %(levelname)s - %(filename)s - %(lineno)d - %(message)s'
)

def main():
  logger = logging.getLogger(__name__)
  

  knowledge_base = ChromaDB()
  ui = CommandLineUI()
  
  study_buddy = StudyBuddy(
    ui=ui, 
    knowledge_base_manager=knowledge_base, 
    logger=logger
  )
  study_buddy.run()

if __name__ == "__main__":
  main()
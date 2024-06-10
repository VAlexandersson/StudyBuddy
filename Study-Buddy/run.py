from study_buddy import StudyBuddy
from db.chroma.chroma_db import ChromaDB
from language_models.transformers.inference_mediator import InferenceMediator
from view.command_line_ui import CommandLineUI
import logging

logging.basicConfig(
    level=logging.DEBUG, 
    format='%(asctime)s - %(levelname)s - %(filename)s - %(lineno)d - %(message)s'
)

def main():
  logger = logging.getLogger(__name__)
  language_model_mediator = InferenceMediator()
  knowledge_base = ChromaDB()
  ui = CommandLineUI()
  study_buddy = StudyBuddy(
    ui=ui, 
    document_retriever=knowledge_base, 
    inference_mediator=language_model_mediator, 
    logger=logger
  )
  study_buddy.run()

if __name__ == "__main__":
  main()
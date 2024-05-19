# app.py
from models.data_models import Query, Response
from logic.tasks.classification.classify_query import ClassifyQueryTask
from logic.tasks.query_processing.decompose_query import DecomposeQueryTask
from logic.tasks.query_processing.preprocess_query import PreprocessQueryTask
from logic.tasks.retrieval.embed_query import EmbedQueryTask
from logic.tasks.retrieval.rerank_documents import ReRankingTask
from logic.tasks.retrieval.filter_documents import FilterDocumentsTask
from logic.tasks.retrieval.retrieve_documents import RetrieveDocumentsTask
from logic.tasks.response.generate_response import GenerateResponseTask
from logic.tasks.response.grade_response import GradeResponseTask
from study_buddy import StudyBuddy

import logging
logging.basicConfig(
    level=logging.DEBUG, 
    format='%(asctime)s - %(levelname)s - %(filename)s - %(lineno)d - %(message)s'
)
logger = logging.getLogger(__name__)

def initialize_components():
  tasks = [
    PreprocessQueryTask,
    ClassifyQueryTask,
    DecomposeQueryTask,
    EmbedQueryTask,
    RetrieveDocumentsTask,
    ReRankingTask,
    FilterDocumentsTask,
    GenerateResponseTask,
    GradeResponseTask,
  ]
  return StudyBuddy(tasks)

def main():
  study_buddy = initialize_components()
  while True:  
    query=Query(text=input("> "))

    if not query.text.strip():
      print("Input is empty, please enter a valid query.")
      continue
    if query.text.lower() == "bye":
      print("bye now!")
      break
    response: Response  = study_buddy.run(query, logger).response
    if not response:
      continue
    print("\n\nQuery: ", query.text)
    print("\nResponse:", response.text)

if __name__ == "__main__":
  main()
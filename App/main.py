# App.main.py
from pipeline.pipeline import Pipeline
from pipeline.data_models import Query, Response
from pipeline.tasks.preprocess_query import PreprocessQueryTask
from pipeline.tasks.classify_query import ClassifyQueryTask
from pipeline.tasks.decompose_query import DecomposeQueryTask
from pipeline.tasks.remove_redundant_documents import DocumentRemoval 
from pipeline.tasks.rerank_documents import ReRankingTask
from pipeline.tasks.retrieve_documents import RetrieveDocumentsTask
from pipeline.tasks.generate_response import GenerateResponseTask
from pipeline.tasks.grade_response import GradeResponseTask

def main():
  tasks = [
    PreprocessQueryTask(),
    ClassifyQueryTask(),
    DecomposeQueryTask(),
    RetrieveDocumentsTask(),
    ReRankingTask(),
    DocumentRemoval(),
    GenerateResponseTask(),
    GradeResponseTask(),
  ]

  pipeline = Pipeline(tasks)

  while True:    
    query = Query(text=input("> "))
    if query.text.lower() == "bye":
      print("bye now!")
      break
    response: Response = pipeline.run(query)
    print("\n\nQuery: ", query)
    print("\n\nResponse:", response.text)

if __name__ == "__main__":
  main()
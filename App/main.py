from pipeline.pipeline import Pipeline
from pipeline.tasks.preprocess_query import PreprocessQueryTask
from pipeline.tasks.classify_query import ClassifyQueryTask
from pipeline.tasks.decompose_query import DecomposeQueryTask
from pipeline.tasks.retrieve_documents import RetrieveDocumentsTask
from pipeline.tasks.rerank_documents import ReRankingTask
from pipeline.tasks.generate_response import GenerateResponseTask
from pipeline.tasks.grade_response import GradeResponseTask

def main():
  pipeline = Pipeline()

  # Add tasks to the pipeline
  pipeline.add_task(PreprocessQueryTask())
  pipeline.add_task(ClassifyQueryTask())
  pipeline.add_task(DecomposeQueryTask())
  pipeline.add_task(RetrieveDocumentsTask())
  pipeline.add_task(ReRankingTask())
  pipeline.add_task(GenerateResponseTask())
  pipeline.add_task(GradeResponseTask())

  while True:
    query = input("> ")
    if query.lower() == "bye":
      print("bye now!")
      break

    result = pipeline.run(query)
    print("\n\nQuery: ", query)
    print("\n\nResponse:", result["response"])

if __name__ == "__main__":
  main()
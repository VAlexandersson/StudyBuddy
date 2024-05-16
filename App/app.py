# app.py
from pipeline.data_models import Query, Response
from pipeline.tasks.preprocess_query import PreprocessQueryTask
from pipeline.tasks.classify_query import ClassifyQueryTask
from pipeline.tasks.decompose_query import DecomposeQueryTask
from pipeline.tasks.retrieve_documents import RetrieveDocumentsTask
from pipeline.tasks.rerank_documents import ReRankingTask
from pipeline.tasks.remove_redundant_documents import DocumentRemoval 
from pipeline.tasks.generate_response import GenerateResponseTask
from pipeline.tasks.grade_response import GradeResponseTask
from study_buddy import StudyBuddy

def initialize_components():
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
    return StudyBuddy(tasks)

def main():
    study_buddy = initialize_components()
    while True:    
        query = Query(text=input("> "))    
        if query.text.lower() == "bye":
            print("bye now!")
            break
        response: Response = study_buddy.run(query)
        print("\n\nQuery: ", query)
        print("\n\nResponse:", response.text)

if __name__ == "__main__":
  main()
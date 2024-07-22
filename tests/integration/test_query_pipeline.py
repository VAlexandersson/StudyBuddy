import pytest
from src.tasks.preprocess_query import PreprocessQueryTask
from src.tasks.classify_query import ClassifyQueryTask
from src.models.context import Context
from src.models.query import Query

class MockClassificationService:
    def classify(self, query, labels, hypothesis_template, multi_label=True):
        return {"labels": ["question"], "scores": [0.9]}

def test_preprocess_and_classify():
    preprocess_task = PreprocessQueryTask("PreprocessQueryTask", {})
    classify_task = ClassifyQueryTask("ClassifyQueryTask", {"classification": MockClassificationService()})
    
    context = Context(query=Query(text="WHAT IS RAG?"))
    context = preprocess_task.run(context)
    context = classify_task.run(context)
    
    assert context.query.text == "what is rag"
    assert context.query.label == "question"
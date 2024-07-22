# tests/tasks/test_preprocess_query.py
import pytest
from src.tasks.preprocess_query import PreprocessQueryTask
from src.models.context import Context
from src.models.query import Query

def test_preprocess_query():
    task = PreprocessQueryTask("PreprocessQueryTask", {})
    context = Context(query=Query(text="HELLO WORLD!"))
    result = task.run(context)
    assert result.query.text == "hello world"
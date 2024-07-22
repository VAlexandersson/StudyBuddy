# tests/tasks/test_preprocess_query.py
import pytest
from src.tasks.preprocess_query import PreprocessQueryTask
from src.models.context import Context
from src.models.query import Query

@pytest.mark.parametrize("input_text,expected_output", [
    ("HELLO WORLD!", "hello world"),
    ("What Is RAG?", "what is rag"),
    ("  Trailing spaces  ", "trailing spaces"),
    ("Multiple     Spaces", "multiple spaces"),
])
def test_preprocess_query(input_text, expected_output):
    task = PreprocessQueryTask("PreprocessQueryTask", {})
    context = Context(query=Query(text=input_text))
    result = task.run(context)
    assert result.query.text == expected_output
# tests/models/test_query.py
import pytest
from src.models.query import Query

def test_query_initialization():
    query = Query(text="What is RAG?")
    assert query.text == "What is RAG?"
    assert query.query_history == []

def test_query_text_setter():
    query = Query(text="Initial query")
    query.text = "Updated query"
    assert query.text == "Updated query"
    assert query.query_history == ["Initial query"]

def test_query_multiple_updates():
    query = Query(text="First query")
    query.text = "Second query"
    query.text = "Third query"
    assert query.text == "Third query"
    assert query.query_history == ["First query", "Second query"]

def test_query_decomposed_parts():
    query = Query(text="Complex query", decomposed_parts=["Part 1", "Part 2"])
    assert query.decomposed_parts == ["Part 1", "Part 2"]

def test_query_label():
    query = Query(text="Query", label="question")
    assert query.label == "question"

def test_query_is_multistep():
    query = Query(text="Multistep query", is_multistep=True)
    assert query.is_multistep == True
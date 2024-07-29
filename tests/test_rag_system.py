# test_rag_system.py
import pytest
from unittest.mock import AsyncMock

from src.models.context import Context
from src.models.query import Query
from src.models.response import Response

@pytest.mark.asyncio
async def test_process_query(rag_system):
    # Mock the task
    mock_task = AsyncMock()
    mock_task.run.return_value = Context(response=Response(text="Processed response"))
    mock_task.get_next_task.return_value = None
    rag_system.tasks["PreprocessQueryTask"] = mock_task

    response = await rag_system.process_query("test query")

    assert response.text == "Processed response"
    #await 
    mock_task.run.assert_called_once()

@pytest.mark.asyncio
async def test_run_task(rag_system):
    mock_task = AsyncMock()
    mock_task.run.return_value = Context(response=Response(text="Task response"))

    context = Context(query=Query(text="test query"))
    new_context = await rag_system._run_task(mock_task, context)

    assert new_context.response.text == "Task response"
    await mock_task.run.assert_called_once_with(context)
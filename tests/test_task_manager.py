import pytest
from src.task_manager import TaskManager
from src.models.context import Context
from src.models.query import Query

class MockTask:
    def __init__(self, name, services):
        self.name = name
        self.services = services

    async def run(self, context):
        context.query.text = f"Processed by {self.name}"
        return context

@pytest.fixture
def mock_config():
    return {
        "TASKS": [
            {
                "name": "MockTask1",
                "class": "tests.test_task_manager.MockTask",
                "services": ["text_generation"]
            },
            {
                "name": "MockTask2",
                "class": "tests.test_task_manager.MockTask",
                "services": ["classification"]
            }
        ],
        "ROUTING": {
            "MockTask1": {
                "default": "MockTask2"
            },
            "MockTask2": {
                "default": "EndTask"
            }
        }
    }

@pytest.fixture
def mock_services():
    return {
        "text_generation_service": "mock_text_gen",
        "classification_service": "mock_classification"
    }

@pytest.fixture
def task_manager(mock_config, mock_services):
    return TaskManager(mock_config, mock_services)

@pytest.mark.asyncio
async def test_task_manager_initialization(task_manager):
    assert "MockTask1" in task_manager.tasks
    assert "MockTask2" in task_manager.tasks
    assert isinstance(task_manager.tasks["MockTask1"], MockTask)
    assert isinstance(task_manager.tasks["MockTask2"], MockTask)

@pytest.mark.asyncio
async def test_task_manager_get_task(task_manager):
    task = task_manager.get_task("MockTask1")
    assert isinstance(task, MockTask)
    assert task.name == "MockTask1"

    with pytest.raises(ValueError):
        task_manager.get_task("NonExistentTask")

@pytest.mark.asyncio
async def test_task_manager_execute_task(task_manager):
    context = Context(query=Query(text="Initial query"))
    result = await task_manager.execute_task("MockTask1", context)
    assert result.query.text == "Processed by MockTask1"

@pytest.mark.asyncio
async def test_task_manager_get_next_task(task_manager):
    next_task = task_manager.get_next_task("MockTask1", "default")
    assert next_task == "MockTask2"

    next_task = task_manager.get_next_task("MockTask2", "default")
    assert next_task == "EndTask"

    next_task = task_manager.get_next_task("NonExistentTask", "default")
    assert next_task == "EndTask"
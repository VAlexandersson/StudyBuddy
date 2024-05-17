from typing import Callable, Optional, Dict
from pipeline.data_models import PipelineContext

Runnable = Callable[[PipelineContext], PipelineContext]

class Task:
    """Represents a task in the processing pipeline."""

    def __init__(self, name: str, function: Runnable, next_tasks: Optional[Dict[str, str]] = None):
        self.name = name
        self.function = function
        self.next_tasks = next_tasks if next_tasks else {}

    def run(self, context: PipelineContext) -> PipelineContext:
        """
        Executes the task's function and updates the pipeline context.
        """
        print(f"Running task: {self.name}")
        return self.function(context)

    def get_next_task(self, routing_key: str) -> Optional[str]:
        """
        Determines the next task to run based on the routing key.
        """
        return self.next_tasks.get(routing_key)
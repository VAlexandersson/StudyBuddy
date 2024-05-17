from typing import Optional, Dict
from pipeline.tasks import Task
from pipeline.data_models import PipelineContext


class DynamicRouter:
    def __init__(self, tasks: Dict[str, Task]):
        self.tasks = tasks

    def get_next_task(self, context: PipelineContext) -> Optional[str]:
        """
        Determines the next task to run based on the context and routing rules.
        """
        if context.query.classification == "course_query" and context.last_task == "ClassifyQueryTask":
            return "RAGTask"
        else:
            return self.tasks.get(context.last_task).get_next_task(context.routing_key)
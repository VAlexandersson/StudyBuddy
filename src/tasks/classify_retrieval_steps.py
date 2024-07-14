from logging import Logger
from src.tasks import Task
from src.models.data_models import Context


class ClassifyQueryTask(Task):
    def run(self, context: Context, logger: Logger) -> Context:
        # Existing classification logic...
        
        # Add complexity classification
        complexity = self.inference_mediator.classify_query(
            context.query.text, 
            ["A", "B", "C"], 
            "This question is of complexity {}:"
        )
        context.query.complexity = max(complexity["labels"], key=lambda x: complexity["scores"][complexity["labels"].index(x)])
        
        # Adjust routing based on complexity
        if context.query.complexity == "A":
            context.routing_key = "generate_response"
        elif context.query.complexity == "B":
            context.routing_key = "single_step_retrieval"
        else:
            context.routing_key = "multi_step_retrieval"
        return context
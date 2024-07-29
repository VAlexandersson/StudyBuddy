from src.utils.logging_utils import logger
from src.tasks import Task
from src.models.context import Context
from src.interfaces.services.text_generation import TextGenerationService
from typing import Dict, Any

class RetrievalEvaluatorTask(Task):
    def __init__(self, name: str, services: Dict[str, Any]):
        super().__init__(name, services)
        self.text_generation_service: TextGenerationService = services['text_generation']

    async def run(self, context: Context) -> Context:
        system_prompt = "You are a retrieval evaluator. Assess the relevance and quality of the retrieved documents in relation to the query. Classify the retrieval as 'Correct', 'Incorrect', or 'Ambiguous'. Answer with a single word."
        user_prompt = f"Query: {context.query.text}\nRetrieved documents:\n{context.retrieved_documents.get_text()}\nClassify the retrieval quality:"
        
        evaluation = await self.text_generation_service.generate_text(
            user_prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.1
        )
        
        context.retrieval_evaluation = evaluation.strip().lower()
        logger.debug(f"Retrieval Evaluation: {context.retrieval_evaluation}")
        return context
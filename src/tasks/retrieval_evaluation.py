from logging import Logger
from src.tasks import Task
from src.models.data_models import Context

class RetrievalEvaluatorTask(Task):
  def run(self, context: Context, logger: Logger) -> Context:
    system_prompt = "You are a retrieval evaluator. Assess the relevance and quality of the retrieved documents in relation to the query. Classify the retrieval as 'Correct', 'Incorrect', or 'Ambiguous'. Answer with a single word."
    user_prompt = f"Query: {context.query.text}\nRetrieved documents:\n{context.retrieved_documents.get_text()}\nClassify the retrieval quality:"
    
    evaluation = self.inference_mediator.generate_response(
      user_prompt=user_prompt,
      system_prompt=system_prompt,
      temperature=0.1
    )
    
    context.retrieval_evaluation = evaluation.strip().lower()
    logger.debug(f"Retrieval Evaluation: {context.retrieval_evaluation}")
    return context
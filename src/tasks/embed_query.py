from logging import Logger
from src.tasks import Task
from src.models.data_models import Context

class EmbedQueryTask(Task):
  def run(self, context: Context, logger: Logger) -> Context:
    context.query.embeddings = self.inference_mediator.encode_query(context.query.text)
    logger.debug(f"Query Embeddings:\n{context.query.embeddings}")
    return context

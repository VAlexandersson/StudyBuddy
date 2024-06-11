from models.data_models import Context
from logging import Logger
from logic import Task

class EmbedQueryTask(Task):
  def run(self, context: Context, logger: Logger) -> Context:
    context.query.embeddings = self.inference_mediator.encode_query(context.query.text)#embedding_model.encode(context.query.text)
    logger.debug(f"Query Embeddings:\n{context.query.embeddings}")
    return context

from models.data_models import PipelineContext
from language_models.sentence_transformer import EmbeddingModel
from logging import Logger
from logic.tasks.base_task import BaseTask

class EmbedQueryTask(BaseTask):
  def run(self, context: PipelineContext, logger: Logger) -> PipelineContext:
    embedding_model = EmbeddingModel()
    context.query.embeddings = embedding_model.encode(context.query.text)
    logger.debug(f"Query Embeddings: {context.query.embeddings}")
    return context

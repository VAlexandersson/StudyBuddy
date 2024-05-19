# App/pipeline/tasks/embed_query.py
from models.data_models import PipelineContext
from language_models.sentence_transformer import EmbeddingModel
from logic.tasks import Task
from logging import Logger

def embed_query(context: PipelineContext, logger: Logger) -> PipelineContext:
  embedding_model = EmbeddingModel()
  context.query.embeddings = embedding_model.encode(context.query.text)
  logger.debug(f"Query Embeddings: {context.query.embeddings}")
  return context

EmbedQueryTask = Task(
  name="EmbedQueryTask",
  function=embed_query,
)
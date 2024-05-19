# App/pipeline/tasks/embed_query.py
from pipeline.data_models import PipelineContext
from models.sentence_transformer import EmbeddingModel
from pipeline.tasks import Task
from logging import Logger

def embed_query(context: PipelineContext, logger: Logger) -> PipelineContext:
  embedding_model = EmbeddingModel()
  context.query.embeddings = embedding_model.encode(context.query.text)
  logger.debug(f"Query Embeddings: {context.query.embeddings}")
  return context

EmbedQueryTask = Task(
  name="EmbedQueryTask",
  function=embed_query,
  next_tasks={
    None: "RetrieveDocumentsTask" 
  }
)
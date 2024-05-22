from models.data_models import PipelineContext
from language_models.cross_encoder import ReRankerModel
from logging import Logger
from logic.tasks.base_task import BaseTask

class ReRankingTask(BaseTask):
  def run(self, context: PipelineContext, logger: Logger) -> PipelineContext:
    cross_encoder = ReRankerModel()  
    query = context.query.text
    documents = context.retrieved_documents.documents

    query_doc_pairs = [(query, doc.document) for doc in documents]
    
    scores = cross_encoder.predict(query_doc_pairs)
    context.retrieved_documents.original_order = [doc.id for doc in documents]

    combined = list(zip(scores, documents))
    combined.sort(key=lambda x: x[0], reverse=True)
    
    documents = [item[1] for item in combined]
    context.retrieved_documents.documents = documents

    logger.debug(f"ReRanked Documents: {documents}")
    
    return context

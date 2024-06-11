from models.data_models import PipelineContext
from logging import Logger
from logic import Task

class ReRankingTask(Task):
  def run(self, context: PipelineContext, logger: Logger) -> PipelineContext:
    query = context.query.text
    documents = context.retrieved_documents.documents

    query_doc_pairs = [(query, doc.document) for doc in documents]
    
    
    scores = self.inference_mediator.rerank_documents(query_doc_pairs) 
    context.retrieved_documents.original_order = [doc.id for doc in documents]

    combined = list(zip(scores, documents))
    combined.sort(key=lambda x: x[0], reverse=True)
    
    documents = [item[1] for item in combined]
    context.retrieved_documents.documents = documents

    logger.debug(f"ReRanked Documents: {documents}")
    
    return context

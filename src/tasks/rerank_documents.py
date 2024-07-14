from logging import Logger
from src.tasks import Task
from src.models.data_models import Context
from src.service.manager import ServiceManager

class ReRankingTask(Task):
  def run(self, context: Context, logger: Logger) -> Context:
    query = context.query.text
    documents = context.retrieved_documents.documents

    query_doc_pairs = [(query, doc.document) for doc in documents]
    print(f"Query Doc Pairs:\n{query_doc_pairs}")
    rerank_service = ServiceManager.get_service('reranking')
    
    scores = rerank_service.rerank(query_doc_pairs) # self.inference_mediator.rerank_documents(query_doc_pairs) 
    context.retrieved_documents.original_order = [doc.id for doc in documents]

    combined = list(zip(scores, documents))
    combined.sort(key=lambda x: x[0], reverse=True)
    
    documents = [item[1] for item in combined]
    context.retrieved_documents.documents = documents

    logger.debug(f"ReRanked Documents: {documents}")
    
    return context

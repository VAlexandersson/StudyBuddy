from pipeline.tasks import Task
from models.cross_encoder import ReRankerModel
from pipeline.data_models import PipelineContext


class ReRankingTask(Task):
  def __init__(self):
    self.cross_encoder = ReRankerModel()

  def run(self, context: PipelineContext, top_k=10) -> PipelineContext:
    query = context.query.text
    documents = context.retrieved_documents.documents

    query_doc_pairs = [(query, doc.document) for doc in documents]
    
    scores = self.cross_encoder.predict(query_doc_pairs)
    context.retrieved_documents.original_order = [doc.id for doc in documents]

    combined = list(zip(scores, documents))
    
    combined.sort(key=lambda x: x[0], reverse=True)
    
    documents = [item[1] for item in combined[:top_k]]
    
    return context


from db.knowledge_base import VectorDB
from models.data_models import PipelineContext, RetrievedDocuments, DocumentObject

from logging import Logger
from logic.tasks.base_task import BaseTask

class RetrieveDocumentsTask(BaseTask):
  def run(self, context: PipelineContext, logger: Logger) -> PipelineContext:
    collection = VectorDB().get_collection()

    # TODO if decomposed_query, retrieve documents for each part of the query
    retrieved_documents = collection.query(
      query_embeddings=context.query.embeddings,
      n_results=10 # top_k
    )
    
    docs = retrieved_documents["documents"][0]
    ids = retrieved_documents["ids"][0]
    metadatas = retrieved_documents["metadatas"][0]

    documents=[DocumentObject(id=id, document=doc, metadatas=metadata) for id, doc, metadata in zip(ids, docs, metadatas)]

    retrieved_documents = RetrievedDocuments(documents=documents)
    
    context.retrieved_documents = retrieved_documents
    logger.debug(f"Retrieved Documents: {retrieved_documents.get_text()}")
    
    return context

from abc import ABC, abstractmethod
from typing import Optional
from models.data_models import PipelineContext
from logging import Logger
from language_models.inference_mediator import InferenceMediator
from knowledge_base.document_retriever import DocumentRetriever

class BaseTask(ABC):
  def __init__(self, name: str, inference_mediator: InferenceMediator, retrieve_documents: DocumentRetriever):
    self.name = name
    self.inference_mediator = inference_mediator
    self.document_retriever = retrieve_documents
    self.routing_config = {}

  @abstractmethod
  def run(self, context: PipelineContext, logger: Logger) -> PipelineContext:
    pass

  def get_next_task(self, routing_key: str) -> Optional[str]:
    return self.routing_config.get(routing_key)

from abc import ABC, abstractmethod
from typing import Optional
from models.data_models import Context
from logging import Logger
from interfaces.language_models import InferenceMediator
from interfaces.knowledge_base import DocumentRetriever

class Task(ABC):
  def __init__(self, name: str, inference_mediator: InferenceMediator, retrieve_documents: DocumentRetriever):
    self.name = name
    self.inference_mediator = inference_mediator
    self.document_retriever = retrieve_documents
    self.routing_config = {}

  @abstractmethod
  def run(self, context: Context, logger: Logger) -> Context:
    pass

  def get_next_task(self, routing_key: str) -> Optional[str]:
    return self.routing_config.get(routing_key)

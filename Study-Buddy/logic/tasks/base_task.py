from abc import ABC, abstractmethod
from typing import Optional
from models.data_models import PipelineContext
from logging import Logger
from language_models.inference_mediator_interface import InferenceMediatorInterface


class BaseTask(ABC):
  def __init__(self, name: str, inference_mediator: InferenceMediatorInterface):
    self.name = name
    self.inference_mediator = inference_mediator
    self.routing_config = {}

  @abstractmethod
  def run(self, context: PipelineContext, logger: Logger) -> PipelineContext:
    pass

  def get_next_task(self, routing_key: str) -> Optional[str]:
    return self.routing_config.get(routing_key)

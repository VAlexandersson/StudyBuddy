from abc import ABC, abstractmethod
from typing import Optional
from models.data_models import PipelineContext
from logging import Logger

class BaseTask(ABC):
  def __init__(self, name: str, **kwargs):
    self.name = name
    self.routing_config = {}

  @abstractmethod
  def run(self, context: PipelineContext, logger: Logger) -> PipelineContext:
    pass

  def get_next_task(self, routing_key: str) -> Optional[str]:
    return self.routing_config.get(routing_key)

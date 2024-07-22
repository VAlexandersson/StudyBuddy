from abc import ABC, abstractmethod
from typing import Optional
from logging import Logger
from src.models.context import Context
from typing import Dict, Any

class Task(ABC):
  def __init__(self, name: str, services: Dict[str, Any]):
    self.name = name
    self.routing_config = {}
    self.services = services

  @abstractmethod
  def run(self, context: Context, logger: Logger) -> Context:
    pass

  def get_next_task(self, routing_key: str) -> Optional[str]:
    return self.routing_config.get(routing_key)

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from logging import Logger
from src.models.context import Context

class Task(ABC):
    def __init__(self, name: str, services: Dict[str, Any]):
      self.name = name
      self.services = services

    @abstractmethod
    async def run(self, context: Context) -> Context:
      pass
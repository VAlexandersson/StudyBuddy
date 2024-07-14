from abc import ABC, abstractmethod
from src.models.data_models import Query, Response

class UserInterface(ABC):
  @abstractmethod
  def get_query(self) -> Query:
      pass

  @abstractmethod
  def post_response(self, response: Response):
      pass
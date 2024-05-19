from abc import ABC, abstractmethod
from models.data_models import Query, Response

class StudyBuddyUI(ABC):
  @abstractmethod
  def get_user_query(self) -> Query:
      pass

  @abstractmethod
  def display_response(self, response: Response):
      pass
from abc import ABC, abstractmethod
from src.models.response import Response

class IOInterface(ABC):
    @abstractmethod
    def get_input(self) -> str:
        pass

    @abstractmethod
    def post_output(self, response: Response):
        pass

    @abstractmethod
    def run(self):
        pass
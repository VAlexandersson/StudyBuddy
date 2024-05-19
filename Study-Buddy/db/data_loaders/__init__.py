from abc import ABC, abstractmethod
class BaseDataLoader(ABC):
    @abstractmethod
    def load_data(self, path: str) -> dict:
        """Loads data from the given path and returns a dictionary containing chunks.
        Args:
            path (str): The path to the data source.
        Returns:
            dict: A dictionary containing the loaded data in a specific format.
        """
        pass
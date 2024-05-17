import json

from db.data_loaders import BaseDataLoader

class JSONDataLoader(BaseDataLoader):
    def load_data(self, path: str) -> dict:
        """Loads data from a JSON file.
        Args:
            path (str): Path to the JSON file.
        Returns:
            dict: A dictionary containing the loaded data, structured as follows:
                {
                  "static_metadata": {
                    "course": ...,
                    "type": ...,
                    "id_code": ...,
                  },
                  "chunks": [
                    {
                      "Chunk": ...,
                      "OrderID": ...,
                      ...
                    },
                    ...
                  ]
                }
        """
        with open(path, 'r') as f:
            data = json.load(f)
        return data
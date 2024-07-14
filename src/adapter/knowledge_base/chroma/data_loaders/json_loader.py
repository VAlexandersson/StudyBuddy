import json
from knowledge_base.chroma.data_loaders import BaseDataLoader

class JSONDataLoader(BaseDataLoader):
    def load_data(self, path: str) -> dict:
        with open(path, 'r') as f:
            data = json.load(f)
        return data
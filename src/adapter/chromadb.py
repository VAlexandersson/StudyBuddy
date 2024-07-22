# src/adapter/knowledge_base/chroma_db.py
import chromadb
import json
from src.service.text_embedder.sentence_transformer import TextEmbedder

PRECHUNKED_DATA = [
    #{
    #    "name": "distributed_system",
    #    "course": "Distributed System",
    #    "type": "book:Distributed Systems 4",
    #    "id": "ds4",
    #    "path": "/home/buddy/Study-Buddy/data/ds4.json",
    #},
    {
        "name": "nutrition_science",
        "course": "Nutrition science",
        "type": "book:Nutrition: Science and Everyday Application",
        "id": "ns",
        "path": "/home/buddy/Study-Buddy/data/nutrition.json",
    }
]


class ChromaDB:
    def __init__(self):
        self.client = chromadb.Client(settings=chromadb.Settings(anonymized_telemetry=False))
        self.embedding_model = TextEmbedder()
        self._initialize_collections()

    def _initialize_collections(self):
        for data_source in PRECHUNKED_DATA:
            if data_source["name"] not in [c.name for c in self.client.list_collections()]:
                self.client.create_collection(
                    data_source["name"], 
                    metadata={
                        "course": data_source["course"],
                        "type": data_source["type"],
                        "id": data_source["id"],
                    }
                )
                self._load_prechunked_data(data_source)

    def _load_prechunked_data(self, data_source):
        print(f"Loading prechunked data_source of course: {data_source['course']}...")
        
        with open(data_source["path"], 'r') as f:
            data = json.load(f)

        chunked_data = {
            "name": data_source["name"], 
            "chunks": data
        }
        self._embed_and_index(chunked_data)

    def _embed_and_index(self, data):
        col_name = data["name"]
        chunks = data["chunks"]
        
        embeddings = self._embed_chunks(chunks)
        self._index_chunks(col_name, chunks, embeddings)

    def _embed_chunks(self, chunks):
        print("Embedding document chunks...")
        text_chunks = [chunk["content"] for chunk in chunks]
        return self.embedding_model.encode_batch(
            text_chunks, 
            batch_size=32, 
            convert_to_tensor=True, 
            show_progress_bar=True
        )

    def _index_chunks(self, collection_name: str, chunks: list, embeddings: list):
        print("Indexing document chunks...")
        collection = self.client.get_collection(collection_name)
        col_id = collection.metadata["id"]
        for i, chunk in enumerate(chunks):
            metadata = {
                **{k: v for k, v in chunk.items() if k != "content" and k != "headings"},
                "heading": chunk["headings"][-1],
            }
            document = chunk["content"]
            doc_id = col_id + "_" + str(chunk["order"])
            embedding_list = embeddings[i].tolist()
            collection.add(
                embeddings=[embedding_list],
                metadatas=[metadata],
                documents=[document],
                ids=[doc_id]
            )
        print(f"Indexed {collection.count()} documents in {collection_name}.")

    def get_client(self):
        return self.client

    def get_embedding_model(self):
        return self.embedding_model
import json
import chromadb
from utils.singleton import Singleton
from models.sentence_transformer import EmbeddingModel

PRECHUNKED_DATA = [
    {
        "course": "Distributed System",
        "type": "book:Distributed Systems 4",
        "id_code": "ds4_",
        "path": "/home/buddy/Study-Buddy/data/ds4.json"
    },
]


@Singleton
class VectorDB():
  def __init__(self):
    self.client = chromadb.Client(settings=chromadb.Settings(anonymized_telemetry=False))  # Initialize Chroma Client
    self.collection = self.client.create_collection(name="course_documents")
    self.embedding_model = EmbeddingModel()
    self.load_prechunked_data()
    print("Knowledge Base Initialized")

  def get_collection(self) -> chromadb.Collection:
    return self.collection

  def load_prechunked_data(self):
    for data in PRECHUNKED_DATA:
      print("Loading prechunked data")
      with open(data["path"], 'r') as f:
        chunks = json.load(f)
      chunked_data = {
        "static_metadata": {
          "course": data["course"],
          "type": data["type"],
          "id_code": data["id_code"],
        },
        "chunks": chunks
      }
      self.embed_and_index(chunked_data)

  def embed_and_index(self, data) -> None:
    print("Embedding and indexing document chunks...")
            
    static_metadata = data["static_metadata"]
    chunks = data["chunks"]
    
    # Extract text chunks from the chunks list
    text_chunks = [chunk["Chunk"] for chunk in chunks]
    
    # Embed texts in batches
    text_chunks_embeddings = self.embedding_model.encode_batch(
      text_chunks, 
      batch_size=32, 
      convert_to_tensor=True, 
      show_progress_bar=True
    )
    
    for i, chunk in enumerate(chunks):
      
      metadata = {
        "course": static_metadata["course"],
        "type": static_metadata["type"],
        **{k: v for k, v in chunk.items() if k != "Chunk"}
      }
      document = chunk["Chunk"]
      doc_id = str(static_metadata["id_code"]) + str(chunk["OrderID"])
      
      # Chroma collection expects the embeddings parameter to be a list of lists
      embedding_list = text_chunks_embeddings[i].tolist()
      
      self.collection.add(
        embeddings=embedding_list,
        metadatas=[metadata],
        documents=[document],
        ids=[doc_id]
      )
    
    print(f"Indexed {self.collection.count()} documents.")

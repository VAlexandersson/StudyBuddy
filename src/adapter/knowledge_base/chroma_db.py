import chromadb
import json
from typing import List
from src.models.document import DocumentObject
from src.interfaces.knowledge_base import KnowledgeBase
from src.adapter.text_embedder.sentence_transformer import TextEmbedder


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

class ChromaDB(KnowledgeBase):
  def __init__(self):
    self.client = chromadb.Client(settings=chromadb.Settings(anonymized_telemetry=False))  # PersistentClient(path='data/chromadb', settings=chromadb.Settings(anonymized_telemetry=False))  # Initialize Chroma Client
    self.collection = [] #self.client.get_or_create_collection(name="course_documents")
    
    self.embedding_model = TextEmbedder()
    for data_source in PRECHUNKED_DATA:
      if data_source["name"] in [c.name for c in self.client.list_collections()]:
        continue
      
      self.client.create_collection(
        data_source["name"], 
        metadata={
          "course": data_source["course"],
          "type": data_source["type"],
          "id": data_source["id"],
        }
      )
      
      #self.collection = self.create_collection(data_source["name"])
      self.load_prechunked_data(data_source)
      
    print("Knowledge Base Initialized")
 
  def get_collection(self) -> chromadb.Collection:
    return self.collection
    
  
  def load_prechunked_data(self, data_source):
    self.collection = self.client.get_or_create_collection(name="course_documents")
    print(f"Loading prechunked data_source of course: {data_source['course']}...")
    
    with open(data_source["path"], 'r') as f:
      data = json.load(f)

    # loader = data_source["loader"]()
    chunked_data = {
      "name": data_source["name"], 
      "chunks": data # loader.load_data(data_source["path"])
    }
    self.embed_and_index(chunked_data)
    #for data_source in PRECHUNKED_DATA:
    #  loader = data_source["loader"]()
    #  chunked_data = {
    #    "static_metadata": {
    #      "course": data_source["course"],
    #      "type": data_source["type"],
    #      "id_code": data_source["id_code"],
    #    },
    #    "chunks": loader.load_data(data_source["path"])
    #  }
    #  self.embed_and_index(chunked_data)

  def _embed_chunks(self, chunks):
    """Embed text chunks in batches."""
    print("Embedding document chunks...")
    text_chunks = [chunk["content"] for chunk in chunks]
    return self.embedding_model.encode_batch(
      text_chunks, 
      batch_size=32, 
      convert_to_tensor=True, 
      show_progress_bar=True
    )

  def _index_chunks(self, collection_name: str, chunks: list, embeddings: list):
    """Index document chunks with metadata and embeddings."""
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
        embeddings=embedding_list,
        metadatas=[metadata],
        documents=[document],
        ids=[doc_id]
      )
    print(f"Indexed {self.collection.count()} documents.")

  def embed_and_index(self, data) -> None:
    """Embed and index document chunks."""
    print("Embedding and indexing document chunks...")

    col_name = data["name"]
    chunks = data["chunks"]
    
    embeddings = self._embed_chunks(chunks)
    
    self._index_chunks(col_name, chunks, embeddings)


  def get_relevant_documents(self, query: str, top_k: int = 10) -> List[DocumentObject]:
    query_embeddings = self.embedding_model.encode(query) 

    retrieved_documents = self.collection.query(
        query_embeddings=query_embeddings,
        n_results=top_k
    )

    docs = retrieved_documents["documents"][0]
    ids = retrieved_documents["ids"][0]
    metadatas = retrieved_documents["metadatas"][0]

    return [DocumentObject(id=id, document=doc, metadatas=metadata) for id, doc, metadata in zip(ids, docs, metadatas)]

  def get_collection_documents(self, query: str, col_name: str, top_k: int = 10) -> List[DocumentObject]:
    collection = self.client.get_collection(col_name)
    query_embeddings = self.embedding_model.encode(query) 

    retrieved_documents = collection.query(
        query_embeddings=query_embeddings,
        n_results=top_k
    )

    print(f"Retrieved Documents: {retrieved_documents}")

    docs = retrieved_documents["documents"][0]
    ids = retrieved_documents["ids"][0]
    metadatas = retrieved_documents["metadatas"][0]

    return [DocumentObject(id=id, document=doc, metadatas=metadata) for id, doc, metadata in zip(ids, docs, metadatas)]
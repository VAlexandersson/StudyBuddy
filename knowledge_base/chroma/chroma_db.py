import chromadb
from typing import List
from interfaces.knowledge_base import KnowledgeBaseManager
from knowledge_base.text_embedder import TextEmbedder
from knowledge_base.chroma.data_loaders.json_loader import JSONDataLoader
from models.data_models import DocumentObject


PRECHUNKED_DATA = [
    {
        "course": "Distributed System",
        "type": "book:Distributed Systems 4",
        "id_code": "ds4_",
        "path": "/home/buddy/Study-Buddy/data/ds4.json",
        "loader": JSONDataLoader
    },
]

class ChromaDB(KnowledgeBaseManager):
  def __init__(self):
    self.client = chromadb.Client(settings=chromadb.Settings(anonymized_telemetry=False))  # Initialize Chroma Client
    self.collection = self.client.create_collection(name="course_documents")
    self.embedding_model = TextEmbedder()
    self.load_prechunked_data()
    print("Knowledge Base Initialized")
 
  def get_collection(self) -> chromadb.Collection:
    return self.collection

  def load_prechunked_data(self):
    for data_source in PRECHUNKED_DATA:
      print("Loading prechunked data_source")
      loader = data_source["loader"]()
      chunked_data = {
        "static_metadata": {
          "course": data_source["course"],
          "type": data_source["type"],
          "id_code": data_source["id_code"],
        },
        "chunks": loader.load_data(data_source["path"])
      }
      self.embed_and_index(chunked_data)

  def _embed_chunks(self, chunks):
    """Embed text chunks in batches."""
    print("Embedding document chunks...")
    text_chunks = [chunk["Chunk"] for chunk in chunks]
    return self.embedding_model.encode_batch(
      text_chunks, 
      batch_size=32, 
      convert_to_tensor=True, 
      show_progress_bar=True
    )

  def _index_chunks(self, chunks: list, static_metadata: dict, embeddings: list):
    """Index document chunks with metadata and embeddings."""
    print("Indexing document chunks...")
    for i, chunk in enumerate(chunks):
      metadata = {
        "course": static_metadata["course"],
        "type": static_metadata["type"],
        **{k: v for k, v in chunk.items() if k != "Chunk"}
      }
      document = chunk["Chunk"]
      doc_id = str(static_metadata["id_code"]) + str(chunk["OrderID"])
      embedding_list = embeddings[i].tolist()
      self.collection.add(
        embeddings=embedding_list,
        metadatas=[metadata],
        documents=[document],
        ids=[doc_id]
      )
    print(f"Indexed {self.collection.count()} documents.")

  def embed_and_index(self, data) -> None:
    """Embed and index document chunks."""
    print("Embedding and indexing document chunks...")
    static_meta = data["static_metadata"]
    chunks = data["chunks"]
    embeddings = self._embed_chunks(chunks)
    self._index_chunks(chunks, static_meta, embeddings)


  def get_relevant_documents(self, query: str, top_k: int = 10) -> List[DocumentObject]:
    # Embed the query within this method
    query_embeddings = self.embedding_model.encode(query) 

    retrieved_documents = self.collection.query(
        query_embeddings=query_embeddings,
        n_results=top_k
    )


    docs = retrieved_documents["documents"][0]
    ids = retrieved_documents["ids"][0]
    metadatas = retrieved_documents["metadatas"][0]

    return [DocumentObject(id=id, document=doc, metadatas=metadata) for id, doc, metadata in zip(ids, docs, metadatas)]

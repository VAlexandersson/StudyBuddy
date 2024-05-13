
from typing import List, Dict
import chromadb
import cohere
import json
from config import PRECHUNKED_DATA, CHROMA_PATH, APP_CONFIG
from dotenv import load_dotenv
import os
from sentence_transformers import SentenceTransformer, util

load_dotenv(override=True)


class RAG:
    def __init__(self, embedding_model: SentenceTransformer, prechunked_data_path: str = None):
        self.embedding_model = embedding_model
        self.co = cohere.Client(os.environ["COHERE_API_KEY"])
        
        self.client     = chromadb.Client(settings=chromadb.Settings(anonymized_telemetry=False))  # Initialize Chroma Client
        self.collection = self.client.create_collection(name="course_documents")

        self.retrieve_top_k = 10
        self.rerank_top_k = 3
        self.load_prechunked_data()

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
        text_chunks_embeddings = self.embedding_model.encode(text_chunks, batch_size=32, convert_to_tensor=True, show_progress_bar=True)
        
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

    def retrieve(self, query: str):
        """
        Embeds a query with model and returns top k scores and indices from embeddings.
        """
        # Embed query
        query_embeddings = self.embedding_model.encode(query, convert_to_tensor=True).tolist()

        # Get results
        results = self.collection.query(query_embeddings=[query_embeddings], n_results=self.retrieve_top_k)
        return results

    def rerank(self, query, docs):
        """Rerank the retrieved documents and returns a list of their ids.

        Args:
            query (str): string query
            docs (List[Dict[str, str]]): List of dicts with the documents and their ids.
            rank_fields (List[str, str]): List of fields to use for reranking. Defaults to None.

        Returns:
            List[str]: List of the retireved documents ids in reranked order.
        """
        
        rerank_results = self.co.rerank(
            query=query,
            documents=docs,
            top_n=self.rerank_top_k,
            model="rerank-english-v3.0",
        )
        
        results = rerank_results.results
         
        reranked_docs_idx = [result.index for result in results]
        return reranked_docs_idx
    
    def advanced(self, query: str, top_k:int=None):
        if top_k: self.rerank_top_k = top_k
        
        retrieved_docs = self.retrieve(query)
        
        docs = retrieved_docs["documents"][0]
        ids = retrieved_docs["ids"][0]
        
        reranked_docs_idx = self.rerank(query=query, docs=docs)
        
        reranked_doc_list = [{"id": ids[idx], "doc": docs[idx]} for idx in reranked_docs_idx]
        
        return reranked_doc_list

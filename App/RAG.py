
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

    def rerank(self, query, docs, rank_fields=None):
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
            rank_fields=rank_fields
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
        

          
        
    def _embed_and_index_cohere(self, data) -> None:
        print("Embedding and indexing document chunks...")

        batch_size = 60  # Adjust batch size as needed MAX 96
        all_embeddings = []
        all_metadatas = []
        all_documents = []
        all_ids = []
        
        static_metadata = data["static_metadata"]
        chunks = data["chunks"]
        
        
        for i in range(0, len(chunks), batch_size):
            batch_chunks = chunks[i: i + batch_size]
            batch_texts = [chunk["Chunk"] for chunk in batch_chunks]
            
            batch_embeddings = self.co.embed(
                texts=batch_texts,
                model="embed-english-v3.0",
                input_type="search_document"
            ).embeddings
            
            batch_metdata = [
                {
                    **static_metadata,
                    **{k: v for k, v in chunk.items() if k != "Chunk"}

                } for chunk in batch_chunks
            ]
            batch_documents = [chunk["Chunk"] for chunk in batch_chunks]
            batch_ids = [static_metadata["id_code"]+int(chunk["OrderID"]) for chunk in batch_chunks]
            
            all_embeddings.extend(batch_embeddings)
            all_metadatas.extend(batch_metdata)
            all_documents.extend(batch_documents)
            all_ids.extend(batch_ids)
            
        self.collection.add( embeddings=all_embeddings, metadatas=all_metadatas, documents=all_documents, ids=all_ids )

        print(f"Indexed {self.collection.count()} documents.")
    def _retrieve_cohere(self, query: str) -> List[Dict[str, str]]:
        """
        Retrieves document chunks based on the given query.

        Parameters:
        query (str): The query to retrieve document chunks for.

        Returns:
        List[Dict[str, str]]: A list of dictionaries representing the retrieved document chunks, with 'title', 'text', and 'url' keys.
        """

        # Dense retrieval
        query_emb = self.co.embed(texts=[query], model="embed-english-v3.0", input_type="search_query").embeddings
        
        results = self.collection.query(query_embeddings=[query_emb], n_results=self.retrieve_top_k)
        
        # Reranking
        rank_fields = ["title", "text"] 

        docs_to_rerank = results.documents  # Access document metadata for reranking

        rerank_results = co.rerank(
            query=query,
            documents=docs_to_rerank,
            top_n=self.rerank_top_k,
            model="rerank-english-v3.0",
            rank_fields=rank_fields
        )

        docs_retrieved = []
        for doc in rerank_results.documents:
            docs_retrieved.append(doc)

        return docs_retrieved
    
    
from pprint import pprint 

def test_rag():
    embedding_model = SentenceTransformer(model_name_or_path=APP_CONFIG["embedding_model_id"], device="cuda")
    # Initialize RAG instance
    rag = RAG(embedding_model)
    rag.load_prechunked_data()

    # Test query
    query = "What is the key difference between a thread and a process?"

    # Retrieve documents based on the query
    retrieved_data = rag.retrieve(query) #retrieve(query)
    pprint(type(retrieved_data))
    
    docs = retrieved_data["documents"][0]
    ids = retrieved_data["ids"][0]
    metadatas = retrieved_data["metadatas"][0]
    pprint(docs)
    
    
    # Print the retrieved documents
    print(f"Retrieved {len(docs)} documents:")
    rank_fields = ["doc"]
    rag.rerank_top_k = 5
    reranked_docs_idx = rag.rerank(query=query, docs=docs)
    doc_list = [{'id': doc_id, 'doc': doc} for doc_id, doc in zip(ids, docs)]

    reranked_doc_list = [doc_list[idx] for idx in reranked_docs_idx]

    compare_ids = [(doc_list[idx]["id"], reranked_doc_list[idx]["id"]) for idx in range(rag.rerank_top_k)]

    pprint(reranked_doc_list)
    pprint(compare_ids)
        
if __name__ == "__main__":
    test_rag()

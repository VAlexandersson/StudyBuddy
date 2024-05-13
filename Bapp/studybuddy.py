
# studybuddy.py

from rag import RAG
from generation import Generation

class StudyBuddy:
    def __init__(self, rag, generation):
        self.rag = rag
        self.generation = generation

    def process_query(self, query):
        retrieved_docs = self.rag.retrieve_and_rerank(query)
        # Perform further processing or pass the retrieved docs to the generation component
        generated_response = self.generation.generate(retrieved_docs)
        return generated_response

    def run(self):
        # Implement the main run loop here
        pass


if __name__ == "__main__":
    # Initialize the embedding model, collection, and reranking model
    embedding_model = ...
    collection = ...
    reranking_model = ...

    rag = RAG(embedding_model, collection, reranking_model)
    generation = Generation(model, tokenizer)

    study_buddy = StudyBuddy(rag, generation)
    study_buddy.run()
import config
from config import CONFIG, SYS_PROMPT, USER_PROMPT
from sentence_transformers import SentenceTransformer, util
from transformers import pipeline
import json
from pydantic import BaseModel, ValidationError
from llms.huggingface_llm import HuggingFaceLLM
from typing import List, Dict
import chromadb
import cohere
from config import PRECHUNKED_DATA, CHROMA_PATH, APP_CONFIG
from llms.huggingface_llm import HuggingFaceLLM
import os

class RAG:
    def __init__( self, embedding_model: SentenceTransformer, prechunked_data_path: str = None ):
        self.embedding_model = embedding_model
        self.co = cohere.Client(os.environ["COHERE_API_KEY"])

        self.client = chromadb.Client(settings=chromadb.Settings(anonymized_telemetry=False))  # Change to persistent client instead.
        self.collection = self.client.create_collection(name="course_documents")

        self.retrieve_top_k = 10
        self.rerank_top_k = 3
        self.load_prechunked_data()

    def store_data(self, data):
        pass

    def load_prechunked_data(self):
        for data in PRECHUNKED_DATA:
            print("Loading prechunked data")
            with open(data["path"], "r") as f:
                chunks = json.load(f)
            chunked_data = {
                "static_metadata": {
                    "course": data["course"],
                    "type": data["type"],
                    "id_code": data["id_code"],
                },
                "chunks": chunks,
            }
            self.embed_and_index(chunked_data)

    def embed_and_index(self, data) -> None:
        print("Embedding and indexing document chunks...")

        static_metadata = data["static_metadata"]
        chunks = data["chunks"]

        # Extract text chunks from the chunks List
        text_chunks = [chunk["Chunk"] for chunk in chunks]

        # Embed texts in batches
        text_chunks_embeddings = self.embedding_model.encode(
            text_chunks, batch_size=32, convert_to_tensor=True, show_progress_bar=True
        )

        for i, chunk in enumerate(chunks):
            metadata = {
                "course": static_metadata["course"],
                "type": static_metadata["type"],
                **{k: v for k, v in chunk.items() if k != "Chunk"},
            }
            document = chunk["Chunk"]
            doc_id = str(static_metadata["id_code"]) + str(chunk["OrderID"])

            # Chroma collection expects the embeddings parameter to be a List of lists
            embedding_list = text_chunks_embeddings[i].tolist()

            self.collection.add(
                embeddings=embedding_list,
                metadatas=[metadata],
                documents=[document],
                ids=[doc_id],
            )

        print(f"Indexed {self.collection.count()} documents.")

    def retrieve(self, query: str):
        """
        Embeds a query with model and returns top k scores and indices from embeddings.
        """
        # Embed query
        query_embeddings = self.embedding_model.encode(
            query, convert_to_tensor=True
        ).tolist()

        # Get results
        results = self.collection.query(
            query_embeddings=[query_embeddings], n_results=self.retrieve_top_k
        )
        return results

    def rerank(self, query, docs):
        """Rerank the retrieved documents and returns a List of their ids.

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

    def advanced(self, query: str, top_k: int = None):
        if top_k:
            self.rerank_top_k = top_k

        retrieved_docs = self.retrieve(query)

        docs = retrieved_docs["documents"][0]
        ids = retrieved_docs["ids"][0]

        reranked_docs_idx = self.rerank(query=query, docs=docs)

        reranked_doc_list = [
            {"id": ids[idx], "doc": docs[idx]} for idx in reranked_docs_idx
        ]

        return reranked_doc_list


class BinaryGrade(BaseModel):
    score: str


class StudyBuddy:
    def __init__(self):
        self.embedding_model = SentenceTransformer(
            model_name_or_path=CONFIG["embedding_model_id"], device=CONFIG["device"]
        )
        self.rag = RAG(self.embedding_model)

        self.zeroshot_classifier = pipeline(
            "zero-shot-classification",
            model="MoritzLaurer/deberta-v3-large-zeroshot-v2.0",
        )
        self.llm = HuggingFaceLLM(model_id=CONFIG["model_id"], device=CONFIG["device"])

        self.chat_history = []
        
        self.query_routes = {
            "course_query": self.vectorstore_query,
            "general_query": self.general_query,
        }


    def format_prompt(self, user_prompt: str, sys_prompt: str):
        message = [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": user_prompt},
        ]
        return message

    def education(self, query: str, docs: List[str]) -> str:
        print("EDUCATION")
        prompt_type = "education"
        documents = "\n- ".join(doc["doc"] for doc in docs)

        sys_prompt = SYS_PROMPT[prompt_type]
        user_prompt = USER_PROMPT[prompt_type].format(query=query, doc=documents)
        finished_prompt = self.format_prompt(
            user_prompt=user_prompt, sys_prompt=sys_prompt
        )

        return self.llm.generate_text(finished_prompt)

    # TODO FIX THIS FUNCTION
    def is_question(self, query: str, verbose: bool = False, max_retries: int = 5) -> BinaryGrade:
        sys_prompt = ""
        user_prompt = f"""
        Please analyze the following query and determine whether it is a question or not. Output your final assessment as a single word ("yes" or "no") in JSON format.

        Query: {query}

        Consider the following factors in your analysis:

        1. Presence of common question words or phrases, such as:
        - Who, What, When, Where, Why, How
        - Do, Does, Did, Will, Would, Should, Can, Could, Is, Are, Am
        - "?"

        2. Structure of the query and whether it follows a typical question format, such as:
        - Starting with a question word or phrase
        - Ending with a question mark
        - Having a subject-verb inversion (e.g., "Is this a question?" instead of "This is a question.")

        3. Context and intent of the query, i.e., whether it seems to be seeking information, clarification, or an answer, or if it appears to be a statement, command, or something else.

        Give a binary 'yes' or 'no' score to indicate whether the answer is a question. 
        Provide the binary score as a JSON with a single key 'score' and no preamble or explanation."""


        prompt = self.format_prompt(user_prompt=user_prompt, sys_prompt=sys_prompt)
        output = self.zeroshot_classifier(
            query,
            ["question", "statement"],
            hypothesis_template="This query is a {}",
            multi_label=True,
        )
        label = output["labels"][0]
        print("classifier output: ", label)
        
        grade = self.binary_grade(prompt)

        return grade

    def binary_grade(
        self, prompt, type: str = None, verbose: bool = False, max_retries: int = 5
    ):
        print("GRADE")
        retries = 0
        while retries < max_retries:
            try:
                message = self.llm.generate_text(prompt)
                
                data = json.loads(message)
                grade = BinaryGrade(score=data["score"])

                if grade.score not in ["yes", "no"]:
                    raise ValueError("Score value must be either 'yes' or 'no'")
            except (ValidationError, ValueError, json.JSONDecodeError) as e:
                print(f"Exception occurred: {str(e)}")
                retries += 1
            else:
                return grade
        print("Max retries reached. Exiting...")
        return None

    def grade_hallucination(
        self, retrieved_documents: List[Dict], response: str
    ) -> BinaryGrade:
        prompt_type = "hallucination"
        print("GRADING HALLUCINATION OF RESPONSE FROM RETRIEVED DOCUMENTS CONTEXT")

        documents = "\n- ".join(doc["doc"] for doc in retrieved_documents)

        sys_prompt = SYS_PROMPT[prompt_type]
        user_prompt = USER_PROMPT[prompt_type].format(
            documents=documents, response=response
        )

        prompt = self.format_prompt(user_prompt=user_prompt, sys_prompt=sys_prompt)

        return self.binary_grade(prompt)

    def grade_answer(self, query: str, response: str) -> BinaryGrade:
        prompt_type = "answer"
        print("GRADING ANSWER")

        sys_prompt = SYS_PROMPT[prompt_type]
        user_prompt = USER_PROMPT[prompt_type].format(query=query, response=response)

        prompt = self.format_prompt(user_prompt=user_prompt, sys_prompt=sys_prompt)

        return self.binary_grade(prompt)

    def grade_relevance(self, query: str, retrieved_document: str, verbose: bool = False) -> BinaryGrade:
        """
        Grades the retrieval of a document based on the query
        """
        prompt_type = "relevance"

        print("GRADING RELEVANCE OF RETRIEVED DOCUMENTS")

        sys_prompt = SYS_PROMPT[prompt_type]
        user_prompt = USER_PROMPT[prompt_type].format(
            doc=retrieved_document, query=query
        )

        prompt = self.format_prompt(user_prompt=user_prompt, sys_prompt=sys_prompt)

        return self.binary_grade(prompt)

    def decompose_query(self, query: str):
        sys_prompt = """You are a query decomposer. Your goal is to break down a user question into distinct sub-questions that need to be answered in order to answer the original question.
        If there are acronyms or words you are not familiar with, do not try to rephrase them.
        Separate the sub-questions with a newline and do not include any additional information or explanations."""

        user_prompt = f"Query: {query}"
        finished_prompt = self.format_prompt(
            user_prompt=user_prompt, sys_prompt=sys_prompt
        )

        message = self.llm.generate_text(finished_prompt)

    def general_query(self, query: str):
        print("General query.")
        sys_prompt = "chitchat with the user based on the query."
        user_prompt = f"Query: {query}"
        finished_prompt = self.format_prompt(
            user_prompt=user_prompt, sys_prompt=sys_prompt
        )

        message = self.llm.generate_text(
            finished_prompt
        )  # add .decode( ) into self.llm.generate_text

        print("\n", message)

    def vectorstore_query(self, query: str):
        print("Vectorstore query.")

        retrieved_docs = self.rag.advanced(query, top_k=10)

        # Filter out the bad docs
        good_docs = [
            doc
            for doc in retrieved_docs
            if self.grade_relevance(query, doc, verbose=False).score == "yes"
        ]

        # If block has page key, -> get parent documents (pages)

        # Summarize the parent docs

        # Validate the summarized parent docs

        documents = "\n- ".join(doc["doc"] for doc in good_docs)

        prompt_type = "education"
        sys_prompt = SYS_PROMPT[prompt_type]
        user_prompt = USER_PROMPT[prompt_type].format(query=query, doc=documents)
        finished_prompt = self.format_prompt(
            user_prompt=user_prompt, sys_prompt=sys_prompt
        )

        message = self.llm.generate_text(
            finished_prompt
        )

        print("\nALLES GUT\n") if self.grade_hallucination(
            good_docs, message
        ).score == "yes" else print("\nALLES SCHEISSE\n")

        print("\n", message)
        
    def course_route(self, query: str):
        output = self.zeroshot_classifier(
            query,
            [
                "distributed systems",
                "machine learning",
                "calculus",
                "planning",
                "schedule",
                "other"
            ],
            hypothesis_template="This query is about the course {}",
            multi_lable=False,
        )
        print(output)
        if output["labels"][0] == "other":
            print("Other")
        elif output["labels"][0] == "distributed systems":
            print("Distributed systems")
            query_function = self.query_routes["course_query"]
            query_function(query)
        
        elif output["labels"][0] == "machine learning":
            print("Machine learning")
        elif output["labels"][0] == "calculus":
            print("Calculus")
        else:
            context = "Aint got shit to do next week."

        pass
    
    def run(self):
        """
        Runs study buddy
        """

        while True:
            query = input("> ")
            if query.lower() == "bye":
                print("Bye to you!")
                break

            # response = self.evaluate_query(query)
            # GENERATE SEARCH QUERIES FOR RAG???? X vs Y. Search for X and Y separated and merge top ranked.

            self.decompose_query(query)

            is_question = self.is_question(query)
            
            if is_question.score == "yes":
                self.course_route(query)
                query_function = self.query_routes["course_query"]
                query_function(query)
                
            elif is_question.score == "no":
                query_function = self.query_routes["general_query"]
                query_function(query)
            


if __name__ == "__main__":
    study_buddy = StudyBuddy()

    study_buddy.run()

import config
from config import CONFIG, SYS_PROMPT, USER_PROMPT

import torch
from sentence_transformers import SentenceTransformer, util
from transformers import AutoTokenizer, AutoModelForCausalLM, TextStreamer, AutoModelForSequenceClassification
from transformers import pipeline
#from RAG import RAG
from pprint import pprint
import json
from pydantic import BaseModel, ValidationError
import time


from typing import List, Dict
import chromadb
import cohere
from config import PRECHUNKED_DATA, CHROMA_PATH, APP_CONFIG
import os



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


class GradeResponse(BaseModel):
    document: dict
    score: str

class Grade(BaseModel):
    score: str


class StudyBuddy:
    def __init__(self): 
        self.embedding_model = SentenceTransformer(model_name_or_path=CONFIG['embedding_model_id'], device=CONFIG['device'])
        os.system('clear')
        
        self.rag = RAG(self.embedding_model)
        
        self.qs_classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
        self.classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
        
        self.tokenizer = AutoTokenizer.from_pretrained(pretrained_model_name_or_path=CONFIG['model_id'])
        self.model = AutoModelForCausalLM.from_pretrained(pretrained_model_name_or_path=CONFIG['model_id'], torch_dtype=torch.float16, low_cpu_mem_usage=False, attn_implementation=CONFIG['attn_implementation']).to(CONFIG['device'])
        self.terminators = [ self.tokenizer.eos_token_id, self.tokenizer.convert_tokens_to_ids("<|eot_id|>") ]
        os.system('clear')
        self.query_routes = {
            "course_query": self.vectorstore_query,
            "general_query": self.general_query,
            "multi_query": self.multi_query,
            "evaluated_query": self.evaluated_query
        }
        
    def generate_message(self, prompt, temperature=0.7):
        #print("daddy chill, im thinking..")
        
        input_ids = self.tokenizer.apply_chat_template(
            prompt,
            add_generation_prompt=True,
            return_tensors="pt"
        ).to("cuda")

        message = self.model.generate(
            input_ids, 
            max_new_tokens=256, 
            eos_token_id=self.terminators,
            temperature=temperature,
            do_sample=True,
            pad_token_id=self.tokenizer.eos_token_id
        )
        # os.system('clear')
        return self.tokenizer.decode(message[0][input_ids.shape[-1]:], skip_special_tokens = True)
    
    def insert_context_into_query(self, query: str, retrieved_documents: list[dict] | dict):
        if isinstance(retrieved_documents, dict):
            retrieved_documents = [retrieved_documents]
        
        base_prompt = f"Query: {query}\nContext:"
        for item in retrieved_documents:
            base_prompt += f"\n- {item['doc']}"
        return base_prompt

    def format_prompt(self, user_prompt: str, sys_prompt: str):
        message = [
            { "role": "system", "content": sys_prompt },
            { "role": "user", "content": user_prompt }
        ]
        return message
    
    def is_question(self, query: str, verbose: bool = False, max_retries: int = 5) -> Grade:
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
        
        print("IS QUESTION------------------\n")

        #inputs = self.q_s_tokenizer(prompt, return_tensors="pt")
        #probablities = self.q_s_model(**inputs).logits
        # tokens = self.q_s_tokenizer(user_prompt)
        # output = self.q_s_model(**tokens)
        prompt = self.format_prompt(user_prompt=user_prompt, sys_prompt=sys_prompt)
        
        start_time_qs_classifier = time.time()
        output = self.qs_classifier(query, ["question", "statement"])
        label = output["labels"][0]
        elapsed_time_qs_classifier = (time.time() - start_time_qs_classifier)*1000

        print(f"qs_classifier execution time: {elapsed_time_qs_classifier} seconds")
        print("q_s output: ", label)
        # time
        print("- - - - - - - - -\n")
        
        # time

        start_time_grade_yes_or_no = time.time()
        grade = self.grade_yes_or_no(prompt)
        elapsed_time_grade_yes_or_no = (time.time() - start_time_grade_yes_or_no)*1000
        print(f"grade_yes_or_no execution time: {elapsed_time_grade_yes_or_no} seconds")
        print(grade)

        # Stop the timer and print the elapsed time
        # print both times
        
        print("------------------\n")
        return grade
    
    
    def grade_yes_or_no(self, prompt: str, type: str = None, verbose: bool=False, max_retries: int=5):
        # print("GRADE")
        retries = 0
        while retries < max_retries:
            try:
                data = json.loads(self.generate_message(prompt, temperature=0.1))
                grade = Grade(score=data["score"])

                if grade.score not in ['yes', 'no']:
                    raise ValueError("Score value must be either 'yes' or 'no'")
            except (ValidationError, ValueError, json.JSONDecodeError) as e:
                print(f"Exception occurred: {str(e)}")
                retries += 1
            else:
                return grade
        print("Max retries reached. Exiting...")
        return None
    
    
    def grade_relevance(self, query: str, retrieved_documents: list[dict], verbose: bool=False):
        prompt_type = "relevance"
        """
        Grades the retrieval of a document based on the query
        """
        
        print("GRADING RELEVANCE OF RETRIEVED DOCUMENTS")
        output = []
        for doc in retrieved_documents:
            

            
            sys_prompt = SYS_PROMPT[prompt_type]
            user_prompt = USER_PROMPT[prompt_type].format(doc=doc["doc"], query = query)
            
            prompt = self.format_prompt(user_prompt=user_prompt, sys_prompt = sys_prompt)
            
            message = self.generate_message(prompt, temperature=0.1)

            score=json.loads(message)

            response = GradeResponse(
                document=doc,
                score=score["score"]
            )
            
            if verbose:
                pprint(response)

            output.append(response)
            
        return output

    def grade_hallucination(self, retrieved_documents: list[dict], response: str) -> Grade:
        prompt_type = "hallucination"
        
        print("GRADING HALLUCINATION OF RESPONSE FROM RETRIEVED DOCUMENTS CONTEXT")

        documents = '\n- '.join(doc['doc'] for doc in retrieved_documents)

        sys_prompt = SYS_PROMPT[prompt_type]
        user_prompt = USER_PROMPT[prompt_type].format(documents=documents, response=response)

        prompt = self.format_prompt(user_prompt=user_prompt, sys_prompt=sys_prompt)
        
        return self.grade_yes_or_no(prompt)
    
    def grade_answer(self, query: str, response: str):
        prompt_type = "answer"
        print("GRADING ANSWER")
        
        sys_prompt = SYS_PROMPT[prompt_type]
        user_prompt = USER_PROMPT[prompt_type].format(query=query, response=response)
        
        prompt = self.format_prompt(user_prompt=user_prompt, sys_prompt=sys_prompt)
        
        message = self.generate_message(prompt, temperature=0.1)
        score=json.loads(message)
        
        return score
    
    
    def multi_query(self, query: str):
        prompt_type = "multi_query"
        print("Multi query------------------\n")
        
        sys_prompt = SYS_PROMPT[prompt_type]
        user_prompt = USER_PROMPT[prompt_type].format(query=query)
        
        prompt = self.format_prompt(user_prompt==user_prompt, sys_prompt=sys_prompt)
        message = self.generate_message(prompt)
        
        print(message)
        print("------------------\n")
        # TODO: Parse the message and return the queries as a list
        
    
    
    def evaluated_query(self, query: str) -> Grade:
        print("Evaluate query.------------------\n")
        
        sys_prompt = """You are query classifier for a RAG module that is used by students in curriculum specific applications.
        Your goal is to determine if a query is curriculum related. 
        Give a binary 'yes' or 'no' score to indicate whether the answer is grounded in supported by a set of facts. 
        Provide the binary score as a JSON with a single key 'score' and no preamble or explanation."""
        
        sys_prompt1 = """You are a query context assessor. Your Goal is to assess if the query needs context to be answered.
        Give a binary 'yes' or 'no' score to indicate whether the query needs context to be answered.
        Provide the binary score as a JSON with a single key 'score' and no preamble or explanation."""
        
        user_prompt = f"Query: {query}"
        
        
        prompt = self.format_prompt(user_prompt=user_prompt, sys_prompt=sys_prompt1)
        grade = self.grade_yes_or_no(prompt)
        print(grade)
        print("------------------\n")
        
        #message = self.generate_message(prompt)
        #score=json.loads(message)["score"]
        #grade = GradeResponse(score=score)
    
        # return grade
    
    def type_query(self, query: str):
        print("------------------\nType query.")
        
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

Final assessment (output as JSON):
{{"isQuestion": "[yes/no]"}}
"""

                
        prompt = self.format_prompt(user_prompt=user_prompt, sys_prompt=sys_prompt)
        message = self.generate_message(prompt)
        
        print(message)
        print("------------------\n")
    
    def extract_keywords(self, query: str):
        print("------------------\nExtract keywords.")
        
        
        sys_prompt = """You are a keyword extractor. Your goal is to identify the main keywords in the given query.
        List the main keywords that you think are important for understanding the query.
        Separate the keywords with commas and do not include any additional information or explanations."""
        
        user_prompt = f"Query: {query}"
        
        prompt = self.format_prompt(user_prompt=user_prompt, sys_prompt=sys_prompt)
        message = self.generate_message(prompt)
        
        print(message)
        print("------------------\n")
    def decompose_query(self, query: str):
        print("------------------")
        print("Decompose query")
        sys_prompt = """You are a query decomposer. Your goal is to break down a user question into distinct sub-questions that need to be answered in order to answer the original question.
        If there are acronyms or words you are not familiar with, do not try to rephrase them.
        Separate the sub-questions with a newline and do not include any additional information or explanations."""
        
        user_prompt = f"Query: {query}"
        finished_prompt = self.format_prompt(user_prompt=user_prompt, sys_prompt=sys_prompt) 
        
        message = self.generate_message(finished_prompt)
        print("\n", message)
        print("------------------\n")
    
    def general_query(self, query: str):
        print("General query.")
        sys_prompt = "chitchat with the user based on the query."
        user_prompt = f"Query: {query}"
        finished_prompt = self.format_prompt(user_prompt=user_prompt, sys_prompt=sys_prompt) 
        
        message = self.generate_message(finished_prompt) # add .decode( ) into generate_message
                    
        print("\n", message)
    
    def vectorstore_query(self, query: str):
        print("Vectorstore query.")
        retrieved_docs = self.rag.advanced(query, top_k = 10)
        grade_response = self.grade_relevance(query, retrieved_docs, verbose=False)
        
        filtered_retrieved_docs = [response.document for response in grade_response if response.score.lower() != 'no']
        
        documents = '\n- '.join(doc['doc'] for doc in filtered_retrieved_docs)
        prompt_type = "education"
        sys_prompt = SYS_PROMPT[prompt_type]
        user_prompt = USER_PROMPT[prompt_type].format(query=query, doc=documents)
        finished_prompt = self.format_prompt(user_prompt=user_prompt, sys_prompt=sys_prompt) 
        message = self.generate_message(finished_prompt) # add .decode( ) into generate_message
                    
        print("\n", self.grade_hallucination(filtered_retrieved_docs , message))
        print("\n", message)

    def route_query(self, query: str):
        """
        Routes the query to the appropriate function based on the query type
        """
        print("Route query")
        query_type = self.determine_query_type(query)
        
        # Is Query is RAGish, Yes or No?
        #   - Is it related to any course?
        
        # If Yes, then RAG it. (use vectorstore)
        
        # If No, then route it to the appropriate function. 
    def determine_query_type(self, query: str):
        """
        Determines the type of query based on the query
        """
        print("Determine query type")
        keyword_mappings = {
            "course_query": ["course", "syllabus", "lecture", "topic", "concept"],
            "general_query": ["what", "how", "when", "where", "why"],
            "multi_query": ["and", "or", "vs", "versus", "compared to"],
            "evaluated_query": ["evaluate", "assessment", "grade", "score"]
        }

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
            
            # grade = self.evaluated_query(query)
            grade = self.is_question(query)
            self.decompose_query(query)
            
            # self.type_query(query)
            # self.extract_keywords(query)
            # self.multi_query(query)
            
            if grade == None:
                continue
            
            if grade.score == "yes":
                query_function = self.query_routes["course_query"]
                query_function(query)
            elif grade.score == "no":
                query_function = self.query_routes["general_query"]
                query_function(query)
            #else:
            #    continue
            continue
                

            retrieved_docs = self.rag.advanced(query, top_k = 10)
            grade_response = self.grade_relevance(query, retrieved_docs, verbose=False)
            filtered_retrieved_docs = [response.document for response in grade_response if response.score.lower() != 'no']
            for response in grade_response:
                #print(response.document)
                print(response.score)
            print(len(filtered_retrieved_docs))
            if False:
                pprint(filtered_retrieved_docs)
                print("\n")
            documents = '\n- '.join(doc['doc'] for doc in filtered_retrieved_docs)
            prompt_type = "education"
            sys_prompt = SYS_PROMPT[prompt_type]
            user_prompt = USER_PROMPT[prompt_type].format(query=query, doc=documents)
            finished_prompt = self.format_prompt(user_prompt=user_prompt, sys_prompt=sys_prompt) 
            message = self.generate_message(finished_prompt) # add .decode( ) into generate_message
            print("\n", self.grade_hallucination(filtered_retrieved_docs , message))            
            print("\n", message)
            print("\n")

if __name__ == "__main__":
    study_buddy = StudyBuddy()
    study_buddy.run()
            
            
            # message = self.generate_message(finished_prompt) # add .decode( ) into generate_message 
            # user_prompt = self.insert_context_into_query(query=query, retrieved_documents=filtered_retrieved_docs)
            
            
            # input_ids = self.tokenizer.apply_chat_template(
            #     finished_prompt,
            #     add_generation_prompt=True,
            #     return_tensors="pt"
            # ).to("cuda")
            # 
            # outputs = self.model.generate(
            #     input_ids, 
            #     max_new_tokens=1024, 
            #     eos_token_id=self.terminators,
            #     do_sample=True,
            #     temperature=0.6,
            #     top_p=0.9,
            #     pad_token_id=self.tokenizer.eos_token_id
            # )
            # streamer = TextStreamer(self.tokenizer, skip_prompt=True, skip_special_tokens=True)
            # _ = self.model.generate(inputs, streamer=streamer, max_new_tokens=1024, eos_token_id=self.terminators, do_sample=True, temperature=0.6, top_p=0.9, pad_token_id=self.tokenizer.eos_token_id)
            
import os
from dotenv import load_dotenv

os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
load_dotenv(override=True)

import torch
CONFIG = {
    'device': 'cuda' if torch.cuda.is_available() else 'cpu',
    'attn_implementation': 'sdpa',
    'model_id': 'meta-llama/Meta-Llama-3-8B-Instruct',
    'embedding_model_id': 'all-mpnet-base-v2',
}

SYS_PROMPT = {

"education": """You are Study-Buddy. An educational chatbot that will aid students in their studies.
You are given the extracted parts of curriculum specific documents and a question. 
Provide a conversational and educational answer with good and easily read formatting.
Give yourself room to think by extracting relevant passages from the context before answering the query.
Don't return the thinking, only return the answer.
If you don't know the answer, just say "I do not know." Don't make up an answer.""",

"relevance": """You are a grader assessing relevance of the context to a user question. 
If the context contains keywords related to the user question, grade it as relevant. It does not need to be a stringent test. The goal is to filter out erroneous retrievals. 
Give a binary score 'yes' or 'no' score to indicate whether the context is relevant to the question. 
Provide the binary score as a JSON with a single key 'score' and no premable or explaination.""",

"hallucination": """You are a grader assessing whether an answer is grounded in supported by a set of facts. 
Give a binary 'yes' or 'no' score to indicate whether the answer is grounded in supported by a set of facts. 
Provide the binary score as a JSON with a single key 'score' and no preamble or explanation.""",

"answer": """You are a grader assessing whether an answer addresses / resolves a question \n
Give a binary score 'yes' or 'no'. Yes' means that the answer resolves the question.""",


"routing": """You are an expert at routing a user query to a vectorstore or web-search.
The vectorstore contains curriculum specific information to courses such as Distributed Systems, Human-Computer Interaction, Examensarbete.
Use the vectorstore for questions on course related queries. Otherwise, use the web-search.
""",

"atomic_rag": """
You are an AI assistant trained to determine if a query can be broken down into multiple queries for better similarity search in a RAG module.
Your goal is to simplify a query by making it atomic. concentrated in one area take the provided query and determine if it could be broken down into multiple atomic queries that is to be used for simmilarity seach in a vectordb. 
Use imperative language and begin each query with an action verb.""",

"classifier": """You are an AI assistant trained to categorize students queries into predefined categories, 
along with sentiment analysis for each category.""",


"decompose": """You are an expert at converting user questions into database queries. \
You have access to a database of course litterature for a wide range of courses. \
Perform query decomposition. Given a user question, break it down into distinct sub questions that \
you need to answer in order to answer the original question.
If there are acronyms or words you are not familiar with, do not try to rephrase them.""",

"is_question": """
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
Provide the binary score as a JSON with a single key 'score' and no preamble or explanation.""",
}

USER_PROMPT = {
    "education": """Query: {query} \n\nContext: {doc}""",
    "relevance": """Here is the retrieved document: \n\n {doc} \n\nHere is the user question: {query}\n""",
    "hallucination": """Here are the facts:\n ------- \n{documents} \n ------- \nHere is the answer: {response} """,
    "multi_query": """Here is the question: {query}""",
    "is_question": "",
    "answer":   "User question: \n\n {question} \n\n LLM generation: {generation}",
    "decompose": """Here is the user question: {question}""",
}

PROMPT = {
}

APP_CONFIG = {
    "llm_model_id": "meta-llama/Meta-Llama-3-8B-Instruct",
    "embedding_model_id": "all-mpnet-base-v2",
    "data_path": "../data",
}

PRECHUNKED_DATA = [
    {
        "course": "Distributed System",
        "type": "book:Distributed Systems 4",
        "id_code": "ds4_",
        "path": "/home/buddy/Study-Buddy/data/manhandled_data/ds4.json"
    },
]

CHROMA_PATH = "../data/vectordb"


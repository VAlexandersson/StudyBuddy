import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import torch
CONFIG = {
    'csv_path': '../data/text_chunks_with_embeddings.csv',
    'device': 'cuda' if torch.cuda.is_available() else 'cpu',
    'attn_implementation': 'sdpa',
    'model_id': 'meta-llama/Meta-Llama-3-8B-Instruct',
    'embedding_model_id': 'all-mpnet-base-v2',
    'system_prompt': """
    You are Study-Buddy. An educational chatbot that will aid students in their studies.
    You are given the extracted parts of curriculum specific documents and a question. Provide a conversational and educational answer with good and easily read formatting.
    Give yourself room to think by extracting relevant passages from the context before answering the query.
    Don't return the thinking, only return the answer.
    If you don't know the answer, just say "I do not know." Don't make up an answer.
    """
}

SYS_PROMPT = {
    "education": """
    You are Study-Buddy. An educational chatbot that will aid students in their studies.
    You are given the extracted parts of curriculum specific documents and a question. Provide a conversational and educational answer with good and easily read formatting.
    Give yourself room to think by extracting relevant passages from the context before answering the query.
    Don't return the thinking, only return the answer.
    If you don't know the answer, just say "I do not know." Don't make up an answer.
    """,
    "relevance": """
    You are a grader assessing relevance of the context to a user question. If the context contains keywords related to the user question, grade it as relevant. It does not need to be a stringent test. The goal is to filter out erroneous retrievals. Give a binary score 'yes' or 'no' score to indicate whether the context is relevant to the question. Provide the binary score as a JSON with a single key 'score' and no premable or explaination.
    """,
    "hallucination": """ You are a grader assessing whether an answer is grounded in supported by a set of facts. 
    Give a binary 'yes' or 'no' score to indicate whether the answer is grounded in supported by a set of facts. Provide the binary score as a JSON with a 
    single key 'score' and no preamble or explanation. 
    """,
}
USER_PROMPT = {
    "relevance": """Here is the retrieved document: \n\n {doc} \n\nHere is the user question: {query}\n""",
    "hallucination": """Here are the facts:\n ------- \n{documents} \n ------- \nHere is the answer: {response} """,
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
        "path": "/home/buddy/Study-Buddy/data/output.json"
    },
]

CHROMA_PATH = "../data/vectordb"
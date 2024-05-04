import os
import torch
from sentence_transformers import SentenceTransformer, util
from transformers import AutoTokenizer, AutoModelForCausalLM

from data_loader import *
from retrieval import *
from config import CONFIG

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
attn_implementation = "sdpa"
model_id = "meta-llama/Meta-Llama-3-8B-Instruct"
embedding_model_id = "all-mpnet-base-v2"

CSV_PATH = "./data/text_chunks_with_embeddings.csv"

chunks_with_embeddings = import_chunks_with_embeddings(CSV_PATH)
embeddings = get_chunks_embeddings_as_tensor(chunks_with_embeddings).to(device)


embedding_model = SentenceTransformer(
    model_name_or_path=embedding_model_id, 
    device=device)

tokenizer = AutoTokenizer.from_pretrained(pretrained_model_name_or_path=model_id)
model = AutoModelForCausalLM.from_pretrained(
    pretrained_model_name_or_path=model_id, 
    torch_dtype=torch.float16,
    low_cpu_mem_usage=False,
    attn_implementation=attn_implementation).to(device)

terminators = [
    tokenizer.eos_token_id,
    tokenizer.convert_tokens_to_ids("<|eot_id|>")
]

system_prompt = """You are Study-Buddy. An educational chatbot that will aid students in their studies.
You are given the extracted parts of curriulum specific documents and a question. Provide a conversational and educational answer with good and easily read formatting.
Give yourself room to think by extracting relevant passages from the context before answering the query.
Don't return the thinking, only return the answer.
If you don't know the answer, just say "I do not know." Don't make up an answer.
"""

class StuddyBuddy:
    def __init__(self):
        self.query_list = query_list
        self.chunks_with_embeddings = import_chunks_with_embeddings(CONFIG['csv_path'])
        self.embeddings = get_chunks_embeddings_as_tensor(
            self.chunks_with_embeddings).to(CONFIG['device'])
        self.embedding_model = SentenceTransformer(
            model_name_or_path=CONFIG['embedding_model_id'], 
            device=CONFIG['device'])
        self.tokenizer = AutoTokenizer.from_pretrained(
            pretrained_model_name_or_path=CONFIG['model_id'])
        self.model = AutoModelForCausalLM.from_pretrained(
            pretrained_model_name_or_path=CONFIG['model_id'], 
            torch_dtype=torch.float16, 
            low_cpu_mem_usage=False, 
            attn_implementation=CONFIG['attn_implementation']
            ).to(CONFIG['device'])
        self.terminators = terminators
        self.system_prompt = CONFIG['system_prompt']

with open('questions.md', 'r') as file:
    query_list = file.read().splitlines()

def get_user_prompt(query: str, retreived_documents: list[dict]):
    """
    Formats the prompt with the query and the retreived documents.
    """
    base_prompt = f"Query: {query}\nContext:"
    for item in retreived_documents:
        base_prompt += f"\n- {item['text']}"
    # base_prompt += [item["text"] for item in retreived_documents]
    
    # context_items = [item for i, item in enumerate(chunks_with_embeddings) if i in indices]
    # prompt = prompt_formatter(query=query, context_items=context_items)
    return base_prompt

def format_prompt(formatted_prompt: str):
    message = [
        { "role": "system", "content": system_prompt },
        { "role": "user", "content": formatted_prompt }
    ]
    return message
    
def generate_response(prompt: str):
    
    input_ids = tokenizer.apply_chat_template(
        prompt,
        add_generation_prompt=True,
        return_tensors="pt"
    ).to("cuda")
    
    outputs = model.generate(
        input_ids, 
        max_new_tokens=1024, 
        eos_token_id = terminators,
        do_sample=True,
        temperature=0.6,
        top_p=0.9,
        pad_token_id=tokenizer.eos_token_id
        
    )
    response = outputs[0][input_ids.shape[-1]:]
    return tokenizer.decode(response)

def study_buddy(query: str):
    scores, indices = retrieve_relevant_resources(query=query, embeddings=embeddings, embedding_model=embedding_model)
    user_prompt = get_user_prompt(query=query, retreived_documents=[chunks_with_embeddings[i] for i in indices])
    formatted_prompt = format_prompt(user_prompt) 
    return generate_response(formatted_prompt)


def run_study_buddy():
    os.system('clear')
    while True:
        query = input("Enter your query (or 'exit' to quit): ")
        if query.lower() == 'exit':
            break
        response = study_buddy(query)
        print(response)


def main():
    # Run the chatbot
    run_study_buddy()

if __name__ == "__main__":
    main()
import torch
from sentence_transformers import SentenceTransformer, util
from transformers import AutoTokenizer, AutoModelForCausalLM

from config import CONFIG
from retrieval import retrieve_relevant_resources
from model_inference import generate_model_response
from data_loader import import_chunks_with_embeddings, get_chunks_embeddings_as_tensor
import importlib

class StudyBuddy:
    def __init__(self, rag: RAG):
        
        self.rag = rag
        
        
        self.chunks_with_embeddings = import_chunks_with_embeddings(CONFIG['csv_path'])
        self.embeddings = get_chunks_embeddings_as_tensor(self.chunks_with_embeddings).to(CONFIG['device'])
        self.embedding_model = SentenceTransformer(model_name_or_path=CONFIG['embedding_model_id'], device=CONFIG['device'])
        self.tokenizer = AutoTokenizer.from_pretrained(pretrained_model_name_or_path=CONFIG['model_id'])
        
        
        self.model = AutoModelForCausalLM.from_pretrained(pretrained_model_name_or_path=CONFIG['model_id'], torch_dtype=torch.float16, low_cpu_mem_usage=False, attn_implementation=CONFIG['attn_implementation']).to(CONFIG['device'])
        self.terminators = [ self.tokenizer.eos_token_id, self.tokenizer.convert_tokens_to_ids("<|eot_id|>") ]
        
    def get_user_prompt(self, query: str, retrieved_documents: list[dict]):
        """
        Formats the prompt with the query and the retreived documents.
        """
        base_prompt = f"Query: {query}\nContext:"
        for item in retrieved_documents:
            base_prompt += f"\n- {item['text']}"
        return base_prompt

    def format_prompt(self, formatted_prompt: str):
        message = [
            { "role": "system", "content": CONFIG['system_prompt'] },
            { "role": "user", "content": formatted_prompt }
        ]
        return message
        
    def generate_response(self, query: str):
        
        scores, indices = retrieve_relevant_resources(
            query=query, 
            embeddings=self.embeddings, 
            embedding_model=self.embedding_model)
        user_prompt = self.get_user_prompt(query=query, retrieved_documents=[self.chunks_with_embeddings[i] for i in indices])
        formatted_prompt = self.format_prompt(user_prompt) 
        return generate_model_response(formatted_prompt, self.tokenizer, self.model, self.terminators)

    def run(self):
        """
        Runs study buddy
        """
        while True:
            
            query = input("> ")
            
            if query.lower("bye"):
                print("Bye to you!")
                break
            
            response = evaluate_query(query)
        
        
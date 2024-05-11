import torch
from sentence_transformers import SentenceTransformer, util
from transformers import AutoTokenizer, AutoModelForCausalLM, TextStreamer

from config import CONFIG
from retrieval import retrieve_relevant_resources
from model_inference import generate_model_response
from RAG import RAG


class StudyBuddy:
    def __init__(self):
        
        self.embedding_model = SentenceTransformer(model_name_or_path=CONFIG['embedding_model_id'], device=CONFIG['device'])
        
        self.rag = RAG(self.embedding_model)
        
        self.tokenizer = AutoTokenizer.from_pretrained(pretrained_model_name_or_path=CONFIG['model_id'])
        self.model = AutoModelForCausalLM.from_pretrained(pretrained_model_name_or_path=CONFIG['model_id'], torch_dtype=torch.float16, low_cpu_mem_usage=False, attn_implementation=CONFIG['attn_implementation']).to(CONFIG['device'])
        self.terminators = [ self.tokenizer.eos_token_id, self.tokenizer.convert_tokens_to_ids("<|eot_id|>") ]
        
    def get_user_prompt(self, query: str, retrieved_documents: list[dict]):
        base_prompt = f"Query: {query}\nContext:"
        for item in retrieved_documents:
            base_prompt += f"\n- {item['doc']}"
        return base_prompt

    def format_prompt(self, formatted_prompt: str):
        message = [
            { "role": "system", "content": CONFIG['system_prompt'] },
            { "role": "user", "content": formatted_prompt }
        ]
        return message

    def evaluated_query(self, query: str):
        print("Evaluate query.")

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
            
            retrieved_docs = self.rag.advanced(query)

            print(f"\n{retrieved_docs}\n")
            
            user_prompt = self.get_user_prompt(
                query=query, 
                retrieved_documents=retrieved_docs# [d['doc'] for d in retrieved_docs if 'doc' in d]
            )
            formatted_prompt = self.format_prompt(user_prompt) 

            #response = generate_model_response(formatted_prompt, self.tokenizer, self.model, self.terminators)
            
            input_ids = self.tokenizer.apply_chat_template(
                formatted_prompt,
                add_generation_prompt=True,
                return_tensors="pt"
            ).to("cuda")
            
            streamer = TextStreamer(self.tokenizer, skip_prompt=True, skip_special_tokens=True)
            
            _ = self.model.generate(input_ids, streamer=streamer, max_new_tokens=1024, eos_token_id=self.terminators, do_sample=True, temperature=0.6, top_p=0.9, pad_token_id=self.tokenizer.eos_token_id)
            
            #outputs = model.generate(
            #    input_ids, 
            #    max_new_tokens=1024, 
            #    eos_token_id=terminators,
            #    do_sample=True,
            #    temperature=0.6,
            #    top_p=0.9,
            #    pad_token_id=tokenizer.eos_token_id
            #)
        #
            #response = outputs[0][input_ids.shape[-1]:]
            #            
            #print(response)


if __name__ == "__main__":
    study_buddy = StudyBuddy()
    study_buddy.run()
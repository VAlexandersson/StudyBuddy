import config
from config import CONFIG, SYS_PROMPT


import torch
from sentence_transformers import SentenceTransformer, util
from transformers import AutoTokenizer, AutoModelForCausalLM, TextStreamer
from retrieval import retrieve_relevant_resources
from model_inference import generate_model_response
from RAG import RAG
from pprint import pprint
import json

class StudyBuddy:
    def __init__(self):
        
        self.embedding_model = SentenceTransformer(model_name_or_path=CONFIG['embedding_model_id'], device=CONFIG['device'])
        
        self.rag = RAG(self.embedding_model)
        
        self.tokenizer = AutoTokenizer.from_pretrained(pretrained_model_name_or_path=CONFIG['model_id'])
        self.model = AutoModelForCausalLM.from_pretrained(pretrained_model_name_or_path=CONFIG['model_id'], torch_dtype=torch.float16, low_cpu_mem_usage=False, attn_implementation=CONFIG['attn_implementation']).to(CONFIG['device'])
        self.terminators = [ self.tokenizer.eos_token_id, self.tokenizer.convert_tokens_to_ids("<|eot_id|>") ]
        
    def insert_context_into_query(self, query: str, retrieved_documents: list[dict] | dict):
        if isinstance(retrieved_documents, dict):
            retrieved_documents = [retrieved_documents]
        
        base_prompt = f"Query: {query}\nContext:"
        for item in retrieved_documents:
            base_prompt += f"\n- {item['doc']}"
        return base_prompt

    def format_prompt(self, prompt: str, sys_role: str="education"):
        message = [
            { "role": "system", "content": SYS_PROMPT[sys_role] },
            { "role": "user", "content": prompt }
        ]
        return message

    def grade_retreival(self, query: str, retrieved_documents: list[dict], verbose: bool=False):
        """
        Grades the retrieval of a document based on the query
        """
        output = []
        for doc in retrieved_documents:
            prompt_context = self.insert_context_into_query(query, [doc])
            prompt = self.format_prompt(prompt=prompt_context, sys_role="relevance")
            # model_prompt = self.tokenizer.apply_chat_template(message, tokenize=True, add_generation_prompt=True, return_tensors="pt").to("cuda")
            
            input_ids = self.tokenizer.apply_chat_template(
                prompt,
                add_generation_prompt=True,
                return_tensors="pt"
            ).to("cuda")
            
            if verbose:
                print("\n---prompt_context---")
                pprint(prompt_context)
                print(f"----------------")
                print("\n---input_ids---")
                pprint(input_ids)
                print(f"---------------")
            
            respond = self.model.generate(
                input_ids, 
                max_new_tokens=256, 
                eos_token_id=self.terminators,
                temperature=0.1,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
        
            output.append(self.tokenizer.decode(respond[0][input_ids.shape[-1]:], skip_special_tokens=True))
            
        return output


    def evaluated_query(self, query: str):
        print("Evaluate query.")

    def run(self):
        """
        Runs study buddy
        """
        
        # Why is achieving full distribution transparency often impractical or even undesirable?

        while True:
            query = input("> ")
            if query.lower() == "bye":
                print("Bye to you!")
                break
            
            # response = self.evaluate_query(query)
            # GENERATE SEARCH QUERIES FOR RAG???? X vs Y. Search for X and Y separated and merge top ranked.
            

                
            retrieved_docs = self.rag.advanced(query, top_k = 10)
            scores = self.grade_retreival(query, retrieved_docs, verbose=False)
            

            for i, item in enumerate(retrieved_docs):
                print(f"{retrieved_docs[i]}")
                print(f"{scores[i]}\n")
                    
            scores = [json.loads(score) for score in scores]

            filtered_retrieved_docs = [doc for i, doc in enumerate(retrieved_docs) if scores[i]["score"] != "no"]
                    
            pprint(filtered_retrieved_docs)        
            print(len(filtered_retrieved_docs))
            
            
            
            user_prompt = self.insert_context_into_query(
                query=query, 
                retrieved_documents=filtered_retrieved_docs# [d['doc'] for d in retrieved_docs if 'doc' in d]
            )
            formatted_prompt = self.format_prompt(user_prompt) 
            
            inputs = self.tokenizer.apply_chat_template(
                formatted_prompt,
                add_generation_prompt=True,
                return_tensors="pt"
            ).to("cuda")
            
            streamer = TextStreamer(self.tokenizer, skip_prompt=True, skip_special_tokens=True)
            #decode_kwargs = dict(inputs, streamer=streamer, max_new_tokens=1024)
            _ = self.model.generate(inputs, streamer=streamer, max_new_tokens=1024, eos_token_id=self.terminators, do_sample=True, temperature=0.6, top_p=0.9, pad_token_id=self.tokenizer.eos_token_id)
            


if __name__ == "__main__":
    study_buddy = StudyBuddy()
    study_buddy.run()
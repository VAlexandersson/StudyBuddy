import config
from config import CONFIG, SYS_PROMPT, USER_PROMPT


import torch
from sentence_transformers import SentenceTransformer, util
from transformers import AutoTokenizer, AutoModelForCausalLM, TextStreamer
from retrieval import retrieve_relevant_resources
from model_inference import generate_model_response
from RAG import RAG
from pprint import pprint
import json
from pydantic import BaseModel

class GradeResponse(BaseModel):
    document: dict
    score: str


class StudyBuddy:
    def __init__(self):
        
        self.embedding_model = SentenceTransformer(model_name_or_path=CONFIG['embedding_model_id'], device=CONFIG['device'])
        
        self.rag = RAG(self.embedding_model)
        
        self.tokenizer = AutoTokenizer.from_pretrained(pretrained_model_name_or_path=CONFIG['model_id'])
        self.model = AutoModelForCausalLM.from_pretrained(pretrained_model_name_or_path=CONFIG['model_id'], torch_dtype=torch.float16, low_cpu_mem_usage=False, attn_implementation=CONFIG['attn_implementation']).to(CONFIG['device'])
        self.terminators = [ self.tokenizer.eos_token_id, self.tokenizer.convert_tokens_to_ids("<|eot_id|>") ]
    
    def generate_message(self, prompt, temperature=0.7):
        
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

        return message[0][input_ids.shape[-1]:]
    
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

    def grade_relevance(self, query: str, retrieved_documents: list[dict], verbose: bool=False):
        """
        Grades the retrieval of a document based on the query
        """
        
        print("GRADING RELEVANCE OF RETRIEVED DOCUMENTS")
        prompt_type = "relevance"
        output = []
        for doc in retrieved_documents:
            user_prompt = USER_PROMPT[prompt_type].format(doc=doc["doc"], query = query)

            prompt = self.format_prompt(prompt=user_prompt, sys_role = prompt_type)
            
            #input_ids = self.tokenizer.apply_chat_template(
            #    prompt,
            #    add_generation_prompt=True,
            #    return_tensors="pt"
            #).to("cuda")
            #message = self.model.generate(
            #    input_ids, 
            #    max_new_tokens=256, 
            #    eos_token_id=self.terminators,
            #    temperature=0.1,
            #    do_sample=True,
            #    pad_token_id=self.tokenizer.eos_token_id
            #)
            
            message = self.generate_message(prompt, temperature=0.1)

            
            
            score=json.loads(self.tokenizer.decode(message, skip_special_tokens=True))

            response = GradeResponse(
                document=doc,
                score=score["score"]
            )
            
            if verbose:
                pprint(response)

            output.append(response)
            
        return output


    def grade_hallucination(self, retrieved_documents: list[dict], response: str):
        prompt_type = "hallucination"
        
        print("GRADING HALLUCINATION OF RESPONSE FROM RETRIEVED DOCUMENTS CONTEXT")
        
        documents = '\n- '.join(retrieved_documents)
        
        user_prompt = USER_PROMPT[prompt_type].format(documents=documents, response=response)
        
        prompt = self.format_prompt(prompt=user_prompt, sys_role=prompt_type)
       
        print(prompt)
        
        
        
        message = self.generate_message(prompt, temperature=0.1)

        score=json.loads(self.tokenizer.decode(message, skip_special_tokens=True))
        return score

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
            grade_response = self.grade_relevance(query, retrieved_docs, verbose=False)
            
            filtered_retrieved_docs = [response.document for response in grade_response if response.score.lower() != 'no']
            
            for response in grade_response:
                #print(response.document)
                print(response.score)
            print(len(filtered_retrieved_docs))
            if False:
                pprint(filtered_retrieved_docs)
                print("\n")
            
            
            user_prompt = self.insert_context_into_query(
                query=query, 
                retrieved_documents=filtered_retrieved_docs
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
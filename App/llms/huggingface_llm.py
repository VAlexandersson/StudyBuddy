from transformers import AutoTokenizer, AutoModelForCausalLM
from llms.base_llm import BaseLLM
import torch
from config import CONFIG

class HuggingFaceLLM(BaseLLM):
    def __init__(self, model_id: str, device: str = "cuda"):
        self.tokenizer = AutoTokenizer.from_pretrained(pretrained_model_name_or_path=CONFIG['model_id'])
        self.model = AutoModelForCausalLM.from_pretrained(pretrained_model_name_or_path=CONFIG['model_id'], torch_dtype=torch.float16, low_cpu_mem_usage=False, attn_implementation=CONFIG['attn_implementation']).to(device)
        self.device = device
        self.terminators = [ self.tokenizer.eos_token_id, self.tokenizer.convert_tokens_to_ids("<|eot_id|>") ]
    
    def generate_text(self, prompt, max_new_tokens: int = 256, temperature: float = 0.7, **kwargs) -> str:
        
        # Tokenize the input
        input_ids = self.tokenizer.apply_chat_template(
            prompt,
            add_generation_prompt=True,
            return_tensors="pt"
        ).to(self.device)
        
        # Generate text
        output = self.model.generate(
            input_ids=input_ids,
            max_new_tokens=1056,
            eos_token_id=self.terminators,
            temperature=temperature,
            do_sample=True,
            pad_token_id=self.tokenizer.pad_token_id,
        )
        
        # Decode the output 
        text = self.tokenizer.decode(output[0][input_ids.shape[-1]:], skip_special_tokens = True)
        return text 

    
    def format_prompt(self, user_prompt: str, sys_prompt: str):

        message = [
            { "role": "system", "content": sys_prompt },
            { "role": "user", "content": user_prompt }
        ]
        return message
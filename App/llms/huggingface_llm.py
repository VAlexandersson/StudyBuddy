from transformers import AutoTokenizer, AutoModelForCausalLM, TextStreamer
from llms.base_llm import BaseLLM

class HuggingFaceLLM(BaseLLM):
    def __init__(self, model_id: str, device: str = "cuda"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        self.model = AutoModelForCausalLM.from_pretrained(model_id).to(device)
        self.device = device
        self.terminators = [ self.tokenizer.eos_token_id, self.tokenizer.convert_tokens_to_ids("<|eot_id|>") ]

    def generate_text(self, prompt: str, max_new_tokens: int = 256, temperature: float = 0.7, **kwargs) -> str:
        
        # Tokenize the input
        input_ids = self.tokenizer(
            prompt, 
            return_tensors="pt"
        ).input_ids.to(self.device)

        # Generate text
        output = self.model.generate(
            input_ids=input_ids,
            max_new_tokens=max_new_tokens,
            eos_token_id=self.terminators,
            temperature=temperature,
            do_sample=True,
            pad_token_id=self.tokenizer.pad_token_id,
        )
        
        # Decode the output 
        generated_text = self.tokenizer.decode(output[0], skip_special_tokens=True)
        return generated_text
    
    def format_prompt(self, user_prompt: str, sys_prompt: str):

        message = [
            { "role": "system", "content": sys_prompt },
            { "role": "user", "content": user_prompt }
        ]
        return message
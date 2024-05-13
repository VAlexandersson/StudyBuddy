from transformers import AutoTokenizer, AutoModelForCausalLM, TextStreamer
from llms.base_llm import BaseLLM

class HuggingFaceLLM(BaseLLM):
    def __init__(self, model_id: str, device: str = "cuda"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        self.model = AutoModelForCausalLM.from_pretrained(model_id).to(device)
        self.device = device

    def generate_text(self, prompt: str, max_new_tokens: int = 256, temperature: float = 0.7, **kwargs) -> str:
        input_ids = self.tokenizer(prompt, return_tensors="pt").input_ids.to(self.device)

        # Generate text
        output = self.model.generate(
            input_ids=input_ids,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            **kwargs,
        )
        
        # Decode the output 
        generated_text = self.tokenizer.decode(output[0], skip_special_tokens=True)
        return generated_text

    def format_prompt(self, user_prompt: str, sys_prompt: str) -> str:
        # Simple prompt formatting for demonstration
        return f"{sys_prompt}\n{user_prompt}"
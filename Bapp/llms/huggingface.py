import torch
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
)

from config import CONFIG
from llms.base_llm import BaseLLM

class FlanT5(BaseLLM):
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained(
            pretrained_model_name_or_path=CONFIG["model_id"]
        )
        self.model = (
            AutoModelForCausalLM.from_pretrained(
                pretrained_model_name_or_path=CONFIG["model_id"],
                torch_dtype=torch.float16,
                low_cpu_mem_usage=False,
                attn_implementation=CONFIG["attn_implementation"],
            )
            .to(CONFIG["device"])
            .eval()
        )
        self.terminators = [
            self.tokenizer.eos_token_id,
            self.tokenizer.convert_tokens_to_ids("<|eot_id|>"),
        ]

    def generate_text(self, prompt, temperature=0.7):
        input_ids = self.tokenizer.apply_chat_template(
            prompt, add_generation_prompt=True, return_tensors="pt"
        ).to("cuda")

        message = self.model.generate(
            input_ids,
            max_new_tokens=256,
            eos_token_id=self.terminators,
            temperature=temperature,
            do_sample=True,
            pad_token_id=self.tokenizer.eos_token_id,
        )
        return self.tokenizer.decode(
            message[0][input_ids.shape[-1] :], skip_special_tokens=True
        )

    def format_prompt(self, user_prompt: str, sys_prompt: str):
        message = [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": user_prompt},
        ]
        return message
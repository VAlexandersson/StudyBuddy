# services/text_generation/transformer_service.py
from .base import TextGenerationService
from language_models.transformers.text_generator import TextGenerator

class TransformerTextGenerationService(TextGenerationService):
    def __init__(self):
        self.text_generator = TextGenerator(model_id = "meta-llama/Meta-Llama-3-8B-Instruct", device = "cuda", attn_implementation = "sdpa")

    def generate_text(self, user_prompt: str, system_prompt: str, temperature: float) -> str:
        return self.text_generator.generate_response(
            user_prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=temperature
        )
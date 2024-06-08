from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

class TextGenerator:
  def __init__(self, model_id: str, device: str, attn_implementation: str):
    self.device = device
    self.tokenizer = AutoTokenizer.from_pretrained(model_id)
    self.model = AutoModelForCausalLM.from_pretrained(
      pretrained_model_name_or_path=model_id,
      torch_dtype=torch.float16,
      low_cpu_mem_usage=False,
      attn_implementation=attn_implementation
    ).to(device)

    self.terminators = [
      self.tokenizer.eos_token_id,
      self.tokenizer.convert_tokens_to_ids("<|eot_id|>")
    ]
    print(f"Loaded Text Generator model: {model_id}")

  def generate_response(self, user_prompt: str, system_prompt: str, temperature: float = 0.7):
    input_text = self._format_prompt(user_prompt, system_prompt)
    response = self._inference(input_text, temperature)
    return response

  def _format_prompt(self, user_prompt: str, system_prompt: str) -> str:
    message = [
      {"role": "system", "content": system_prompt},
      {"role": "user", "content": user_prompt}
    ]
    return message
  
  def _inference(self, input_text, temperature: float = 0.7):

    # Tokenize the input
    input_ids = self.tokenizer.apply_chat_template(
      input_text,
      add_generation_prompt=True,
      return_tensors='pt'
    )

    # Type checking
    if not isinstance(input_ids, torch.Tensor):
      input_ids = torch.tensor(input_ids)
    input_ids = input_ids.to(self.device)

    # Generate text
    output = self.model.generate(
      input_ids=input_ids,
      max_new_tokens=1056,
      eos_token_id=self.terminators,
      temperature=temperature,
      do_sample=True,
      pad_token_id=self.tokenizer.eos_token_id,
    )

    # Decode the output
    text = self.tokenizer.decode(
      output[0][input_ids.shape[-1]:],
      skip_special_tokens=True
    )
    return text
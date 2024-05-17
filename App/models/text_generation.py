from transformers import AutoTokenizer, AutoModelForCausalLM
from utils.singleton import Singleton
from utils.format_prompt import format_prompt
import torch


@Singleton
class LLM:
  """
  (singleton) Language Learning Model (LLM) class for generating responses based on a given query and context.

  Args:
    model_id (str): The identifier of the pre-trained language model to be used.
    device (str): The device to run the model on (e.g., "cuda" for GPU or "cpu" for CPU).
    attn_implementation (str): The attention implementation to be used by the model.

  Attributes:
    device (str): The device to run the model on.
    tokenizer (AutoTokenizer): The tokenizer for the language model.
    model (AutoModelForCausalLM): The pre-trained language model.
    terminators (list): List of token IDs representing sentence terminators.

  Methods:
    generate_response(query, documents=None, temperature=0.7):
      Generates a response based on the given query and optional context documents.

    format_prompt(user, system):
      Formats the user and system prompts into a message.

  """

  def __init__(self, model_id: str = "meta-llama/Meta-Llama-3-8B-Instruct", device: str = "cuda", attn_implementation: str = "sdpa"):
    """
    Initializes the LLM object.

    Args:
      model_id (str): The identifier of the pre-trained language model to be used.
      device (str): The device to run the model on (e.g., "cuda" for GPU or "cpu" for CPU).
      attn_implementation (str): The attention implementation to be used by the model.
    """

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


  def generate_response(self, user: str, system: str, temperature: float = 0.7):
    input_text = format_prompt(user, system)
    response = self.inference(input_text, temperature)
    return response

  def inference(self, input_text, temperature: float = 0.7):
    """
    Generates a response based on the given query and optional context documents.

    Args:
      query (str): The query for which a response is to be generated.
      documents (list): Optional list of context documents.
      temperature (float): The temperature value for controlling the randomness of the generated text.

    Returns:
      str: The generated response.

    """

    # Tokenize the input
    input_ids = self.tokenizer.apply_chat_template(
      input_text,
      add_generation_prompt=True,
      return_tensors='pt'
    )

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
      pad_token_id=self.tokenizer.pad_token_id,
    )

    # Decode the output
    text = self.tokenizer.decode(
      output[0][input_ids.shape[-1]:],
      skip_special_tokens=True
    )
    return text
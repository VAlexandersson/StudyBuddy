from config.prompt_library import RELEVANCE_PROMPT, STANDARD_PROMPT, PROMPT



def format_prompt(user: str, system: str) -> list[dict[str, str]]:
  """
  Formats the user and system prompts into a message.

  Args:
    user (str): The user prompt.
    system (str): The system prompt.

  Returns:
    list: The formatted message containing the user and system prompts.

  """

  message = [
    {"role": "system", "content": system},
    {"role": "user", "content": user}
  ]
  return message

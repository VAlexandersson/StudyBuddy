import json

def binary_grade(user_prompt, system_prompt, max_retries: int = 5, temperature: int = 0.01) -> str | None:
  """
  Generates a binary grade based on user and system prompts.

  Args:
    user_prompt (str): The user prompt.
    system_prompt (str): The system prompt.
    max_retries (int, optional): The maximum number of retries. Defaults to 5.
    temperature (int, optional): The temperature for text generation. Defaults to 0.01.

  Returns:
    str | None: The generated binary grade ('yes' or 'no') or None if max retries are reached.
  """
  retries = 0

  #text_gen_service = ServiceManager.get_service('text_generation')

  while retries < max_retries:
    message = "asd" #text_gen_service.generate_text( 
    #  user_prompt=user_prompt,
    #  system_prompt=system_prompt,
    #  temperature=temperature
    #)
    try:
      data = json.loads(message)
      grade = data["score"]

      if grade not in ["yes", "no"]:
        raise ValueError("Score value must be either 'yes' or 'no'")
    except (ValueError, json.JSONDecodeError) as e:
      print(f"Exception occurred: {str(e)}")
      retries += 1
    else:
      return grade
  print("Max retries reached. Exiting...")
  return None
  
def format_prompt(user: str, system: str) -> list[dict[str, str]]:
  message = [
    {"role": "system", "content": system},
    {"role": "user", "content": user}
  ]
  return message

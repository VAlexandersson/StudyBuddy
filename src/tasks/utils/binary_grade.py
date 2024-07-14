import json

def binary_grade(message, max_retries: int = 5) -> str | None:
  retries = 0
  while retries < max_retries:
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

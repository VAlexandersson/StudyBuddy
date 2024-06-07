import json
from pydantic import BaseModel, ValidationError
from language_models.text_generation import LLM

class BinaryGrade(BaseModel):
  score: str

def binary_grade(prompt, type: str = None, max_retries: int = 5):
  retries = 0
  llm = LLM()
  while retries < max_retries:
    try:
      message = llm.inference(prompt)
        
      data = json.loads(message)
      grade = BinaryGrade(score=data["score"])

      if grade.score not in ["yes", "no"]:
          raise ValueError("Score value must be either 'yes' or 'no'")
    except (ValidationError, ValueError, json.JSONDecodeError) as e:
      print(f"Exception occurred: {str(e)}")
      retries += 1
    else:
      return grade
  print("Max retries reached. Exiting...")
  return None

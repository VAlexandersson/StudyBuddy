
from src.tasks.tools.binary_grade import binary_grade
from src.interfaces.services.text_generation import TextGenerationService

async def binary_grade_document_relevance(doc: str, query:str, text_generation_service: TextGenerationService):  # # the document is completely unrelated
#  system_prompt = """Assess if the document is relevant to the user's query and can be used as a source to answer it. 
#
#Give a simple 'yes' or 'no' answer:
#- 'yes' if the document contains any information related to the query
#- else 'no'
#
#Respond with only this JSON format:
#{"score": "yes"} or {"score": "no"}
#""", 
#  user_prompt = f"Retrieved document: \n\n {doc} \n\nQuery: {query}\n"


  system_prompt = """You are tasked with identifying passages that contain the specific information needed to answer a question. 

Does this passage contain the specific facts or details needed to directly answer the question? Answer with only 'yes' or 'no'. 

Respond with only this JSON format:
{"score": "yes"} or {"score": "no"}
"""



  asd = f"""Assess if the retrieved document contains information directly relevant to answering the query: {query}.

Give a simple 'yes' or 'no' answer:
- 'yes' if the document contains specific information about the key aspect of the query
- 'no' if the document doesn't address these aspects or only mentions them tangentially

Respond with only this JSON format:
{{"score": "yes"}} or {{"score": "no"}}
"""
  #user_prompt= f"Retrieved document:\n{doc}"
  user_prompt=f"Passage: \n\n {doc} \n\nQuery: {query}\n",
  grade = await binary_grade(
    user_prompt=user_prompt,
    system_prompt=system_prompt, 
    text_gen_service=text_generation_service
  )



  return grade
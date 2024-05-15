from config.prompt_library import RELEVANCE_PROMPT
from pipeline.tasks import Task
from models.text_generation import LLM
from utils.binary_grade import binary_grade
from utils.format_prompt import format_prompt


class DocumentRemoval(Task):
  def __init__(self):
    self.llm = LLM()

  def run(self, data):
    user_prompt, system_prompt = RELEVANCE_PROMPT
    query = data['query']
    documents = data['reranked_documents']
    #reranked_documents = [doc.document for doc in data['reranked_documents']]
    #context = "\n- ".join(reranked_documents)
    grades = []
    for context in documents:
      prompt = format_prompt(user = user_prompt.format(context.document, query), system=system_prompt)
      grades.append(binary_grade(prompt))

    print(grades)
    return {
      "query": query, 
      "reranked_documents": documents,
      "grades": grades,
      "decomposed_query": data["decomposed_query"], 
      "classification": data["classification"]
    }

    #return [doc for doc in documents if not doc.get('redundant')]
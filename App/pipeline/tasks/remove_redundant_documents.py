# App.pipeline.tasks.remove_redundant_documents.py
from pipeline.tasks import Task
from models.text_generation import LLM
from utils.binary_grade import binary_grade
from utils.format_prompt import format_prompt
from config.prompt_library import RELEVANCE_PROMPT
from pipeline.data_models import ReRankedDocuments, GradedDocuments 

class DocumentRemoval(Task):
  def __init__(self):
    self.llm = LLM()

  def run(self, reranked_documents: ReRankedDocuments) -> GradedDocuments:
    
    user_prompt, system_prompt = RELEVANCE_PROMPT
    query = reranked_documents.query.text
    documents = reranked_documents.documents

    grades = []
    for context in documents:
      prompt = format_prompt(
        user = user_prompt.format(context.document, query), 
        system=system_prompt
      )
      grades.append(binary_grade(prompt).score)
    print(grades)
    return GradedDocuments(query=reranked_documents.query, documents=documents, grades=grades)

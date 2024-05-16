# App.pipeline.tasks.remove_redundant_documents.py
from pipeline.tasks import Task
from models.text_generation import LLM
from utils.binary_grade import binary_grade
from utils.format_prompt import format_prompt
from config.prompt_library import RELEVANCE_PROMPT
from pipeline.data_models import PipelineContext 

class DocumentRemoval(Task):
  def __init__(self):
    self.llm = LLM()

  def run(self, context: PipelineContext) -> PipelineContext:
    user_prompt, system_prompt = RELEVANCE_PROMPT
    context.retrieved_documents.ignore = []
    for doc in context.retrieved_documents.documents:
      prompt = format_prompt(
        user = user_prompt.format(doc, context.query.text), 
        system=system_prompt
      )
      context.retrieved_documents.ignore.append(binary_grade(prompt).score)
    print(context.retrieved_documents.ignore)
    #GradedDocuments(query=context.query, documents=documents, grades=grades)
    return context
from config.prompt_library import STANDARD_PROMPT
from pipeline.tasks import Task
from models.text_generation import LLM
from utils.concat_documents import concat_documents
from pipeline.data_models import GradedDocuments, Response

class GenerateResponseTask(Task):
  def __init__(self):
    self.llm = LLM()
    
  def run(self, graded_documents: GradedDocuments) -> Response:
    user_prompt, system_prompt = STANDARD_PROMPT

    query = graded_documents.query.text
    documents = graded_documents.documents

    context = concat_documents(documents)
    
    response_text = self.llm.generate_response(
      user = user_prompt.format(query, context), 
      system = system_prompt
    )

    print("\n\nResponse: ", response_text)
    
    return Response(query=graded_documents.query, text=response_text)
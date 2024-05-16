from config.prompt_library import STANDARD_PROMPT
from pipeline.tasks import Task
from models.text_generation import LLM
from utils.concat_documents import concat_documents
from utils.format_prompt import format_prompt
from pipeline.data_models import PipelineContext, Response

class GenerateResponseTask(Task):
  def __init__(self):
    self.llm = LLM()
    
  def run(self, context: PipelineContext) -> PipelineContext:
    print("Generating response...")

    if context.query.classification == "general_query":
      context.response = Response(text=self.llm.inference(format_prompt(context.query.text, "Be nice.")))
      #documents = context.documents if context.query.classification == "course_query" else ""
    else:
      user_prompt, system_prompt = STANDARD_PROMPT

      context_document_text = concat_documents(context.retrieved_documents.documents)
      user_prompt.format(context.query.text, context_document_text)
      context.response = Response(text=self.llm.inference(format_prompt(user=user_prompt, system=system_prompt)))
    return context
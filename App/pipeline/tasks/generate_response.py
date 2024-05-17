# pipeline/tasks/generate_response.py
from config.prompt_library import STANDARD_PROMPT
from pipeline.data_models import PipelineContext, Response
from models.text_generation import LLM
from utils.concat_documents import concat_documents
from utils.format_prompt import format_prompt

from pipeline.tasks import Task


def generate_response(context: PipelineContext) -> PipelineContext:
  print("Generating response...")
  llm = LLM() 

  if context.query.classification == "general_query":
    context.response = Response(text=llm.inference(format_prompt(context.query.text, "Be nice.")))
  else:
    user_prompt, system_prompt = STANDARD_PROMPT
    context_document_text = concat_documents(context.retrieved_documents.documents)
    user_prompt.format(context.query.text, context_document_text)
    context.response = Response(text=llm.inference(format_prompt(user=user_prompt, system=system_prompt)))
  return context

GenerateResponseTask = Task(
  name="GenerateResponseTask",
  function=generate_response,
  next_tasks={
      None: "GradeResponseTask"
  }
)
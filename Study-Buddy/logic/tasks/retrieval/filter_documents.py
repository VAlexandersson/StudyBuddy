from configs.prompt_library import RELEVANCE_PROMPT
from models.data_models import PipelineContext 
from utils.binary_grade import binary_grade
from utils.format_prompt import format_prompt
from logic.tasks import Task
from logging import Logger

def filter_documents(context: PipelineContext, logger: Logger) -> PipelineContext:
  user_prompt, system_prompt = RELEVANCE_PROMPT

  for doc in context.retrieved_documents.documents:
    prompt = format_prompt(
      user = user_prompt.format(doc, context.query.text), 
      system=system_prompt
    )
    context.retrieved_documents.ignore.append(binary_grade(prompt).score)
  
  no_indices = [i for i, x in enumerate(context.retrieved_documents.ignore) if x == 'no']
  context.retrieved_documents.filtered_documents = [context.retrieved_documents.documents[i] for i in no_indices]
  context.retrieved_documents.documents = [doc for i, doc in enumerate(context.retrieved_documents.documents) if i not in no_indices]

  logger.debug(f"Filtered Documents: {context.retrieved_documents.filtered_documents}")

  return context

FilterDocumentsTask = Task(
  name="FilterDocumentsTask",
  function=filter_documents,
)
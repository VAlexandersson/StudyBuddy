from typing import List
from logging import Logger
from logic.tasks import Task
from models.data_models import PipelineContext, Response
from view.study_buddy_ui import StudyBuddyUI
from logic.tasks.classification.classify_query import ClassifyQueryTask
from logic.tasks.query_processing.decompose_query import DecomposeQueryTask
from logic.tasks.query_processing.preprocess_query import PreprocessQueryTask
from logic.tasks.retrieval.embed_query import EmbedQueryTask
from logic.tasks.retrieval.rerank_documents import ReRankingTask
from logic.tasks.retrieval.filter_documents import FilterDocumentsTask
from logic.tasks.retrieval.retrieve_documents import RetrieveDocumentsTask
from logic.tasks.response.generate_response import GenerateResponseTask
from logic.tasks.response.grade_response import GradeResponseTask

class StudyBuddy:
  def __init__(self, ui: StudyBuddyUI):
    self.tasks = self._initialize_tasks()
    self.ui = ui
    
  def _initialize_tasks(Self):
    tasks = [
      PreprocessQueryTask,
      ClassifyQueryTask,
      DecomposeQueryTask,
      EmbedQueryTask,
      RetrieveDocumentsTask,
      ReRankingTask,
      FilterDocumentsTask,
      GenerateResponseTask,
      GradeResponseTask,
    ]
    return {task.name: task for task in tasks}

  def run(self, logger: Logger) -> PipelineContext:
    while True:
      query = self.ui.get_user_query()
      if not query.text.strip():
        continue
      if query.text.lower() == "exit":
        self.ui.display_response(Response(text="Goodbye!"))
        break
      
      context = PipelineContext(query=query)
      current_task = self.tasks["PreprocessQueryTask"] 

      while current_task:
        context = current_task.run(context, logger)
        logger.info(f"Routing Key: {context.routing_key}") 
        next_task_name = current_task.get_next_task(context.routing_key)
        logger.info(f"Next Task: {next_task_name}")
        current_task = self.tasks.get(next_task_name)
        logger.info(f"Current Task: {current_task}")
        context.routing_key = None # reset routing key

      self.ui.display_response(context.response)
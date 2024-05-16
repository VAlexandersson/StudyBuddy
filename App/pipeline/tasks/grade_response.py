from pipeline.tasks import Task
from pipeline.data_models import PipelineContext
# TODO Implement the logic
class GradeResponseTask(Task):
  def __init__(self):
    pass
  def run(self, context: PipelineContext) -> PipelineContext:
    print("Grade")
    context.response.grade = "A"
    return context
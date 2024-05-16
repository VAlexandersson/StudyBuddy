from pipeline.tasks import Task
from pipeline.data_models import Response
# TODO Implement the logic
class GradeResponseTask(Task):
  def run(self, response: Response) -> Response:
    print("Grade")
    response.grade = "A"
    return response
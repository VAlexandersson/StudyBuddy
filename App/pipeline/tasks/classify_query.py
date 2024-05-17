
from pipeline.data_models import PipelineContext
from models.zero_shot_classifier import ZeroShotClassifier

from pipeline.tasks import Task


def classify_query(context: PipelineContext) -> PipelineContext:
    classifier = ZeroShotClassifier()
    classification = classifier.classify(
        context.query.text,
        labels=["course_query", "general_query", "search_the_web"]
    )
    print(f"Classification: {classification}")
    context.query.classification = classification
    context.routing_key = classification
    return context


ClassifyQueryTask = Task(
    name="ClassifyQueryTask",
    function=classify_query,
    next_tasks={
        "course_query": "DecomposeQueryTask",
        "general_query": "GenerateResponseTask",
        "search_the_web": "SearchTheWebTask",
    }
)
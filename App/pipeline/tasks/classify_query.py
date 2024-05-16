from pipeline.tasks import Task
from pipeline.data_models import PipelineContext
from models.zero_shot_classifier import ZeroShotClassifier

class ClassifyQueryTask(Task):
    def __init__(self):
        self.classifier = ZeroShotClassifier()

    def run(self, context: PipelineContext) -> PipelineContext:
        classification = self.classifier.classify(context.query.text)
        print(f"Classification: {classification}")
        context.query.classification = classification
        context.routing_key = classification
        return context
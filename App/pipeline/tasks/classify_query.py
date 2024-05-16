from pipeline.tasks import Task
from pipeline.data_models import Query
from models.zero_shot_classifier import ZeroShotClassifier

class ClassifyQueryTask(Task):
    def __init__(self):
        self.classifier = ZeroShotClassifier()

    def run(self, query: Query) -> Query:
        classification = self.classifier.classify(query.text)
        query.classification = classification
        return query
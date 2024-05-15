from pipeline.tasks import Task
from models.zero_shot_classifier import ZeroShotClassifier

class ClassifyQueryTask(Task):
    def __init__(self):
        self.classifier = ZeroShotClassifier()

    def run(self, query):
        classification = self.classifier.classify(query)
        return {"query": query, "classification": classification}
from pipeline.tasks import Task

class ClassifyQueryTask(Task):
    def run(self, query):
        # TODO logic
        classification = "general" # (Remove)
        
        return {"query": query, "classification": classification}
from pipeline.tasks import Task

class PreprocessQueryTask(Task):
    def run(self, query):
        # TODO: logic
        preprocessed_query = query.lower()
        return preprocessed_query
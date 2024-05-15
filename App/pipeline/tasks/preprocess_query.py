from pipeline.tasks import Task
from utils.text_preprocessing import preprocess_text

class PreprocessQueryTask(Task):
    def run(self, query):
        # TODO: logic
        preprocessed_query = preprocess_text(query)
        return preprocessed_query
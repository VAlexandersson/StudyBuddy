from pipeline.tasks import Task

class DecomposeQueryTask(Task):
    def run(self, data):
        query = data["query"]
        # TODO logic
        decomposed_query = [query]  # REMOVE
        return {
            "query": query, 
            "decomposed_query": decomposed_query, 
            "classification": data["classification"]
        }
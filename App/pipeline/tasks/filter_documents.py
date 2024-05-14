from pipeline.tasks import Task

class FilterDocumentsTask(Task):
    def run(self, data):
        retrieved_documents = data["retrieved_documents"]
        # TODO logic
        filtered_documents = retrieved_documents  # Remove
        return {
            "query": data["query"], 
            "filtered_documents": filtered_documents, 
            "decomposed_query": data["decomposed_query"], 
            "classification": data["classification"]
        }
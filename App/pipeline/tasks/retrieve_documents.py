from pipeline.tasks import Task

class RetrieveDocumentsTask(Task):
    def run(self, data):
        query = data["query"]
        # TODO logic
        retrieved_documents = []  # Remove
        return {
            "query": query, 
            "retrieved_documents": retrieved_documents, 
            "decomposed_query": data["decomposed_query"], 
            "classification": data["classification"]
        }
from pipeline.tasks import Task

class GenerateResponseTask(Task):
    def run(self, data):
        query = data["query"]
        filtered_documents = data["filtered_documents"]
        # TODO logic
        response = "This is a generated response."  # Remove
        return {
            "query": query, 
            "response": response, 
            "filtered_documents": filtered_documents, 
            "decomposed_query": data["decomposed_query"], 
            "classification": data["classification"]
        }
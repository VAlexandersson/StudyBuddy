from pipeline.tasks import Task

class GradeResponseTask(Task):
    def run(self, data):
        query = data["query"]
        response = data["response"]
        # TODO logic
        grade = "A"  # Remove
        return {
            "query": query, 
            "response": response, 
            "grade": grade, 
            "reranked_documents": data["reranked_documents"], 
            "decomposed_query": data["decomposed_query"], 
            "classification": data["classification"]
        }
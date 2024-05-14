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
            "filtered_documents": data["filtered_documents"], 
            "decomposed_query": data["decomposed_query"], 
            "classification": data["classification"]
        }
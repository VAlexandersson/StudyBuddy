
class Pipeline:
    def __init__(self):
        self.tasks = []

    def add_task(self, task):
        self.tasks.append(task)

    def run(self, query):
        data = query
        for task in self.tasks:
            data = task.run(data)
        return data
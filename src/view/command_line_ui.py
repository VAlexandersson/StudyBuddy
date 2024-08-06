import asyncio
from src.rag_system import RAGSystem
from src.models.response import Response
from src.models.context import Context
from src.models.query import Query
from src.models.document import RetrievedDocuments

class CommandLineUI:
    def __init__(self, rag_system: RAGSystem):
        self.rag_system = rag_system

    async def get_input(self) -> str:
        return await asyncio.get_event_loop().run_in_executor(None, input, "User: ")

    def post_output(self, context: Context):
        response = context.response.text
        print(f"Assistant: {response}")

    async def run(self):
        while True:
            user_input = await self.get_input()
            if user_input.lower() in ['exit', 'quit']:
                break
            response = await self.rag_system.process_query(user_input)
            self.post_output(response)
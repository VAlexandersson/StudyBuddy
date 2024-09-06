from src.utils.logging_utils import logger
from src.models.context import Context
from src.models.response import Response
from src.tasks import Task
from src.interfaces.services.text_generation import TextGenerationService
from typing import Dict, Any

class GenerateResponseTask(Task):
    def __init__(self, name: str, services: Dict[str, Any]):
        super().__init__(name, services)
        self.text_generation_service: TextGenerationService = services['text_generation']

    async def run(self, context: Context) -> Context:
        print("\n")
        logger.debug(f"\n\tQuery:\n{context.query.text}\n\tLabel:\n{context.query.label}")
        system_prompt = "You are Study Buddy. An assistant for students to use in their studies. You're responses are concise with no fluff."
        
        response_text = await self.text_generation_service.generate_text(
            user_prompt=context.query.text,
            system_prompt=system_prompt,
            temperature=0.7
        )

        if context.query.label in ["question", "command"]:
          not_grounded_notice = "[!NOTICE] !RESPONSE NOT GROUNDED! ANSWER MAY NOT BE RELIABLE.[!NOTICE]\n\n"
          response_text = not_grounded_notice + response_text + "\n\n" + not_grounded_notice
        
        context.response = Response(text=response_text)
        print(f"\n\tResponse:\n{context.response.text}\n")
        return context
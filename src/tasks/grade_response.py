from src.utils.logging_utils import logger
from src.models.context import Context
from src.tasks import Task
from src.tasks.utils.binary_grade import binary_grade
from src.tasks.utils.prompt_library import HALLUCINATION_PROMPT
from src.interfaces.services.text_generation import TextGenerationService
from typing import Dict, Any



class GradeResponseTask(Task):
    def __init__(self, name: str, services: Dict[str, Any]):
      super().__init__(name, services)
      self.text_generation_service: TextGenerationService = services['text_generation']

    async def run(self, context: Context) -> Context:
        system_prompt, user_prompt = HALLUCINATION_PROMPT
        user_prompt = user_prompt.format(documents=context.retrieved_documents.get_text(), response=context.response.text)

        grade = await binary_grade(user_prompt=user_prompt, system_prompt=system_prompt, text_gen_service=self.text_generation_service)
        
        logger.debug(f"Response Grade: {grade}")
        print(f"Response Grade: {grade}")
        #TODO: FALLBACK ROUTE, If the response is graded as 'no', we will try again to provide a better response

        return context
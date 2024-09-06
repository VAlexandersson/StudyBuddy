from src.tasks import Task
from src.models.context import Context
from src.interfaces.services.text_generation import TextGenerationService
from typing import Dict, Any

SYSTEM_PROMPT = """You are Study-Buddy. An educational chatbot that will aid students in their studies.
You are given a query asked by a student and extracted parts of curriculum specific documents as context to the query.

For each piece of information you use, cite the passages using their ID's (e.g., [ns_146]).
Incorporate the information from the provided sources without explicitly referencing them in your response. Cite each piece of information using only the passage ID in square brackets at the end of the relevant sentence or paragraph. Do not use phrases like "According to the provided context" or "The given information states." Instead, present the information as if it's part of your own knowledge base, while still providing proper citation.
For example: "This elliptical orbit takes approximately 365.25 days to complete [ns_201]. And the text continues while still being cited... [ns_202]"
Your final answer should be detailed, cohesive, and directly grounded in the provided documents.

Your process is split into 2 steps, THINKING and WRITING:
- THINKING: is for planning the reply
- WRITING: is for generating the response


CURRENT STEP: {step}

{instructions}

{step_instruction}
"""

THINKING_INSTRUCTIONS = """Reflect on the query and the context. 
Reflect on the following:
- What the query is strictly asking about
- How to structure the response
- Reflect over the different passages in the context and how they can be used to answer the query without extraneous information.
- Explicitly mention each passage by their ID and reason to why it can be used for answering the query or why it can not.

The instructions should be without any noise, like leading or trailing "redundant text"."""


WRITING_INSTRUCTIONS = "Generate a response that focuses on the query that is detailed, cohesive, and grounded in the provided documents. Take your earlier reflection into consideration you made earlier, in the THINKING step, that can be found enclosed with the XML-tags `<THINKING>`."

class TwoStepResponseGenerationTask(Task):
  def __init__(self, name: str, services: Dict[str, Any]):
      super().__init__(name, services)
      self.text_generation_service: TextGenerationService = services['text_generation']


  async def run(self, context: Context) -> Context:

    query = context.query.text
    
    user_prompt = f"""Query: {query} \n\Context: {[{'id': doc.id, 'document': doc.transformed_document} for doc in context.retrieved_documents.documents]}"""

    thinking_step = SYSTEM_PROMPT.format(step="THINKING", instructions='', step_instruction=THINKING_INSTRUCTIONS)
    
    thinking = await self.text_generation_service.generate_text(
        user_prompt=user_prompt,
        system_prompt=thinking_step,
        temperature=0.4
    )
    print(f"\nTHINKING STEP:\n{thinking}\n\n")

    writing_step = SYSTEM_PROMPT.format(step="WRITING", instructions="<THINKING>"+thinking+"</THINKING>", step_instruction=WRITING_INSTRUCTIONS)
    response = await self.text_generation_service.generate_text(
        user_prompt=user_prompt,
        system_prompt=writing_step,
        temperature=0.5
    )

    print(f"\RESPONSE:\n{response}\n\n")
    
    context.response.text = response
    return context

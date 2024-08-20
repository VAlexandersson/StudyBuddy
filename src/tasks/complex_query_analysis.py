from src.tasks import Task
from src.models.context import Context
from src.interfaces.services.text_generation import TextGenerationService
from src.interfaces.services.document_retrieval import DocumentRetrievalService
from src.models.document import DocumentObject
from typing import Dict, Any, List
import json
from src.tasks.tools.binary_grade import binary_grade
from src.tasks.tools.binary_grade_document_relevance import binary_grade_document_relevance
from src.tasks.tools.query_focused_summary import query_focused_summary

class ComplexQueryAnalysisTask(Task):
  def __init__(self, name: str, services: Dict[str, Any]):
      super().__init__(name, services)
      self.text_generation_service: TextGenerationService = services['text_generation']
      self.document_retrieval_service: DocumentRetrievalService = services['document_retrieval']


  async def run(self, context: Context) -> Context:
      print(f"QUERY: {context.query.text}")

      query = context.query.text

      indices_to_remove = []

      for i, doc in enumerate(context.retrieved_documents.documents):
        print(f"DOCUMENT: {doc.id}\n{doc.document}")

        grade = await binary_grade_document_relevance(doc, query, self.text_generation_service)

        print(f"GRADE: {grade}")

        if grade == 'no':
          print(f"Document {doc.id} is not relevant to the query.")
          indices_to_remove.append(i)

      for index in sorted(indices_to_remove, reverse=True):
        doc = context.retrieved_documents.documents.pop(index)
        context.retrieved_documents.filtered_documents.append(doc)
        print(f"Removed document at index {index} with id {doc.id}")

      for doc in context.retrieved_documents.documents:

        summary = await query_focused_summary(query, doc.document, self.text_generation_service)
        doc.transformed_document = summary
        
      print([{'id': doc.id, 'document': doc.transformed_document} for doc in context.retrieved_documents.documents])

      user_prompt = f"""Query: {query} \n\Context: {[{'id': doc.id, 'document': doc.transformed_document} for doc in context.retrieved_documents.documents]}"""

      system_prompt = """You are Study-Buddy. An educational chatbot that will aid students in their studies.
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

#Produce instructions for your self that shall outline a plan for next step WRITING.

#Your response should outline an easily adaptable plan for the WRITING step to follow.

      thinking_prompt = """Reflect on the query and the context. 
Reflect on the following:
- What the query is strictly asking about
- How to structure the response
- Reflect over the different passages in the context and how they can be used to answer the query without extraneous information.
  - Explicitly mention each passage by their ID and reason to why it can be used for answering the query or why it can not.

The instructions should be without any noise, like leading or trailing "redundant text"."""
      thinking_step = system_prompt.format(step="THINKING", instructions='', step_instruction=thinking_prompt)
      thinking = await self.text_generation_service.generate_text(
          user_prompt=user_prompt,
          system_prompt=thinking_step,
          temperature=0.4
      )
      print(f"\nTHINKING STEP:\n{thinking}\n\n")

      writing_prompt = "Generate a response that focuses on the query that is detailed, cohesive, and grounded in the provided documents. Take your earlier reflection into consideration you made earlier, in the THINKING step, that can be found enclosed with the XML-tags `<THINKING>`."
      writing_step = system_prompt.format(step="WRITING", instructions="<THINKING>"+thinking+"</THINKING>", step_instruction=writing_prompt)
      writing = await self.text_generation_service.generate_text(
          user_prompt=user_prompt,
          system_prompt=writing_step,
          temperature=0.5
      )

      print(f"\nWRITING STEP:\n{writing}\n\n")
      
      system_prompt = """You are Study-Buddy. An educational chatbot that will aid students in their studies.
You are given a query asked by a student and extracted parts of curriculum specific documents as context to the query.

For each piece of information you use, cite the source with IEEE format using the passage's IDs (e.g., [ns_146]).
Incorporate the information from the provided sources without explicitly referencing them in your response. Cite each piece of information using only the passage ID in square brackets at the end of the relevant sentence or paragraph. Do not use phrases like "According to the provided context" or "The given information states." Instead, present the information as if it's part of your own knowledge base, while still providing proper citation.
For example: "This elliptical orbit takes approximately 365.25 days to complete [ns_201]. And the text continues while still being cited... [ns_202]"
Your answer should be detailed, cohesive, and directly grounded in the provided documents.
"""
      user_prompt = f"""Query: {query} \n\nContext: {[{'id': doc.id, 'document': doc.transformed_document} for doc in context.retrieved_documents.documents]}"""
      final_response = writing #await self.text_generation_service.generate_text(user_prompt=user_prompt, system_prompt=system_prompt, temperature=0.7 )

      print(f"\tFINAL RESPONSE:\n{final_response}\n")

      system_prompt = """You're a robot that can explicitly only reply with instructions formatted as bulleted list.
Review the response generated by the chatbot and assess if it is relevant to the user's query and if it is coherent, informative and well structured.

Create instructions for the chatbot to improve the response while only using the context of the retrieved documents.

Reply only with the instructions in a bulleted list format."""

#      user_prompt = f"""Query: {query} \nRetrieved documents: {[{'id': doc.id, 'document': doc.transformed_document} for doc in context.retrieved_documents.documents]}, \nResponse: {final_response}"""
#
#      instructions = await self.text_generation_service.generate_text(
#          user_prompt=user_prompt,
#          system_prompt=system_prompt,
#          temperature=0.6
#      )
#
#      print(f"\tINSTRUCTIONS:\n{instructions}\n\n")


      system_prompt = """You are Study-Buddy. An educational chatbot that will aid students in their studies.

You will be given:
- A query asked by a student
- Extracted parts of curriculum specific documents as context to the query
- A draft response generated by an AI
- Instructions on how to improve the response

You are to improve a response generated by the chatbot by following the instructions (if you deem them necessary) provided by the previous AI.

Reply only with the revised response that is directly focused on the query and is detailed, cohesive, and grounded in the context.
"""

#      user_prompt = f"""Query: {query}\n\nContext: {[{'id': doc.id, 'document': doc.transformed_document} for doc in context.retrieved_documents.documents]}\n\nDraft response: {final_response}\n\n Instructions: {instructions}"""
#
#      revised_response = await self.text_generation_service.generate_text(
#          user_prompt=user_prompt,
#          system_prompt=system_prompt,
#          temperature=0.6
#      )
#
#      print(f"\nREVISED RESPONSE:\n{revised_response}\n\n")



      context.response.text = final_response
      return context

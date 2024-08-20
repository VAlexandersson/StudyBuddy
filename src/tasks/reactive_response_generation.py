from src.tasks import Task
from src.models.context import Context
from src.interfaces.services.text_generation import TextGenerationService
from src.models.document import DocumentObject
from typing import Dict, Any, List
import json
from src.tasks.tools.binary_grade import binary_grade
from src.tasks.tools.binary_grade_document_relevance import binary_grade_document_relevance
from src.tasks.tools.query_focused_summary import query_focused_summary

class ReActiveResponseGeneration(Task):
  def __init__(self, name: str, services: Dict[str, Any]):
      super().__init__(name, services)
      self.text_generation_service: TextGenerationService = services['text_generation']


  async def run(self, context: Context) -> Context:
      # Step 1: Analyze query
      print(f"QUERY: {context.query.text}")

      query = context.query.text
      relevant_docs = context.retrieved_documents.documents

      query = context.query.text

      final_response_draft = await self.synthesize_contextual_response(query, relevant_docs)

      print(f"\tFINAL RESPONSE DRAFT:\n{final_response_draft}\n")

      system_prompt = """Review the response generated by the chatbot and assess if it is relevant to the user's query and if it is coherent, informative and well structured.

Create instructions for the chatbot to improve the response while only using the textual context of the retrieved documents.

Explicitly only reply with the instructions that is formatted in bulleted list."""

      user_prompt = f"Query: {query}\nRetrieved documents: {[{"doc_id": doc.id, "document": doc.transformed_document} for doc in relevant_docs]}\nResponse: {response}"

      instructions = await self.text_generation_service.generate_text(
          user_prompt=user_prompt,
          system_prompt=system_prompt,
          temperature=0.6
      )

      print(f"\tINSTRUCTIONS:\n{instructions}\n\n")

      context.response.text = final_response_draft
      return context

  async def synthesize_contextual_response(self, query: str, documents: List[DocumentObject]) -> str:
    system_prompt = """You are Study-Buddy. An educational chatbot that will aid students in their studies.
You are given a query asked by a student and extracted parts of curriculum specific documents as context to the query.

For each piece of information you use, cite the source using the passage ID (e.g., [as_99]).
Incorporate the information from the provided sources without explicitly referencing them in your response. Cite each piece of information using only the passage ID in square brackets at the end of the relevant sentence or paragraph. Do not use phrases like "According to the provided context" or "The given information states." Instead, present the information as if it's part of your own knowledge base, while still providing proper citation.
For example: "This elliptical orbit takes approximately 365.25 days to complete [as_1201]. And the text continues while still being cited... [as_202]".

Your answer should be detailed, cohesive, and directly grounded in the provided documents.
"""
    user_prompt = f"Query: {query}\nRetrieved documents: {[{"doc_id": doc.id, "document": doc.transformed_document} for doc in documents]}"

    
    response = await self.text_generation_service.generate_text(
        user_prompt=user_prompt,
        system_prompt=system_prompt,
        temperature=0.7
    )

    return response

  async def reactive_improve(self, query: str, documents: List[DocumentObject], response: str) -> str:

    context_relevance_grade = await self.binary_grade_response_context_relevance(query)

    if context_relevance_grade["score"] == "yes":
      sys_relevance_instruction = """The response generated by the chatbot has been deemed not comprehensive or accurate based on the provided context documents. Provide instructions to the chatbot on how to improve the response using the context documents."""
      user_relevance_instruction = f"Query: {query}\nRetrieved documents: {documents}\nResponse: {response}"


  async def binary_grade_response_context_relevance(self, query: str) -> Dict:
    system_prompt = """Assess if the AI's response to the user's query can be improved based on the provided context documents. 

Give a simple 'yes' or 'no' answer:
- 'yes' if there are any significant omissions, inaccuracies, or areas where the response could be enhanced using information from the context documents
- 'no' if the response is comprehensive, accurate, and effectively utilizes all relevant information from the context documents

Respond with only this JSON format:
{"score": "yes"} or {"score": "no"}
"""
    user_prompt = f"Query: {query}\nRetrieved documents: {[{"doc_id": doc.id, "document": doc.transformed_document} for doc in relevant_docs]}\nResponse: {response}"

    context_relevance_grade = await binary_grade(
      user_prompt=user_prompt,
      system_prompt=system_prompt, 
      text_gen_service=self.text_generation_service
    )
    
    return context_relevance_grade
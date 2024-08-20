import json
from src.interfaces.services.text_generation import TextGenerationService

async def query_focused_summary(query: str, document: str, text_generation_service: TextGenerationService) -> str:
  prompt = f"""Query: {query}\nText to summarize:\n{document}"""

  response = await text_generation_service.generate_text(
    user_prompt=prompt,
    system_prompt = """You are a robot that is built to summarize texts, focusing specifically on information relevant to answering provided query.

The information should strictly adhere to the query.
        
Respond with only a JSON containing only the summary of the text.
Example:
{"summary": "summary of text"}
""",
    temperature=0.3,
  )
  summary = json.loads(response)
  return summary["summary"]
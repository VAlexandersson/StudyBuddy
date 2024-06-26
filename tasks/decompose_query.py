from models.data_models import Context
from logging import Logger
from tasks import Task

class DecomposeQueryTask(Task):
  def run(self, context: Context, logger: Logger):
    user_prompt = """
    User's question: {}

    Sub-queries:
    """.format(context.query.text)
    system_prompt = """
You are an AI assistant tasked with breaking down complex queries into simpler sub-queries. Given a user's question, your job is to:
1. Identify the main components of the query
2. Create 2-4 simpler sub-queries that together address all aspects of the original question
3. Ensure each sub-query is self-contained and can be answered independently
4. Output the sub-queries in a numbered list
"""

    decomposed_query = self.inference_mediator.generate_response(
        user_prompt=user_prompt,
        system_prompt=system_prompt,
        temperature=0.1,
    )
    context.query.decomposed_parts = decomposed_query.split('\n')

    logger.debug(f"Decomposed Query: {context.query.decomposed_parts}")

    return context

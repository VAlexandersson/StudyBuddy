# Study-Buddy

Title: Study Buddy: An AI-Powered Chatbot for Student Assistance

1. Introduction
   - Study Buddy is an AI chatbot designed to assist students by answering questions and providing relevant information.
2. Input
   - The chatbot accepts user queries in text format.
3. Pipeline Processing

    3.1. Preprocess Query
     - The input query is cleaned and standardized to optimize processing.
 
    3.2. Classify Query
     - The chatbot classifies the query as either "course_query" (related to specific coursework) or "general_query" (more general knowledge).
 
    3.3. Dynamic Routing

       3.3.1. For "course_query":
         - Retrieval-Augmented Generation (RAG) approach is used.
         - Relevant documents are fetched from a knowledge base.
         - Redundant or less relevant documents are removed to enhance efficiency.
         - Remaining documents are reordered based on their relevance to the query.
       
       3.3.2. For "general_query":
         - The RAG process is skipped, and the chatbot proceeds directly to response generation.
    3.4. Generate Response
      - The chatbot generates a textual response using a language model (LLM).
      - The response considers the query and relevant documents (if applicable).
  
    3.5. Grade Response
      - The generated response is assessed for quality and potential hallucinations (factual inaccuracies) using the LLM.

4. Output

   - The chatbot presents the generated response to the user.
   - A grade indicating the response's quality is provided.

5. Configurable Pipeline
   - The chatbot's pipeline is highly configurable through:
     - Dedicated Context Methods: Enable organized and readable data management within the pipeline.
     - Dynamic Routing: Control the pipeline flow based on query type and other conditions.
     - External Configuration: Routing rules are defined in a YAML file for easy modification without code changes.
6. Future Enhancements

   - More Complex Routing Logic: Introduce intricate routing rules based on user preferences, query complexity, or data availability.
   - User Profiles: Incorporate user-specific information to personalize responses.
   - Interactive Learning: Make the chatbot more interactive by asking clarifying questions or suggesting learning resources based on user responses.


## Papers:

| Paper                                                                                                 | link                             |
| ----------------------------------------------------------------------------------------------------- | -------------------------------- |
| Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection                        | https://arxiv.org/abs/2310.11511 |
| Adaptive-RAG: Learning to Adapt Retrieval-Augmented Large Language Models through Question Complexity | https://arxiv.org/abs/2403.14403 |
| Corrective Retrieval Augmented Generation                                                             | https://arxiv.org/abs/2401.15884 |
|                                                                                                       |                                  |
|                                                                                                       |                                  |

### Embeddings and Reranking:

[Reranking Leaderboard](https://huggingface.co/spaces/AIR-Bench/leaderboard)

[BGE M3-Embedding: Multi-Lingual, Multi-Functionality, Multi-Granularity Text Embeddings Through Self-Knowledge Distillation](https://arxiv.org/abs/2402.03216)
[Making Large Language Models A Better Foundation For Dense Retrieval](https://arxiv.org/abs/2312.15503)

## Study Buddy

### Introduction

Study Buddy is a chatbot designed to assist students with their academic studies. The chatbot uses a flexible pipeline architecture, leveraging language models and information retrieval techniques to provide relevant and informative responses to user queries. 

### Features

- **Curriculum-Specific Knowledge:** The chatbot can be customized with a knowledge base containing information relevant to specific courses or academic subjects.
- **Retrieval-Augmented Generation (RAG):** For course-related queries, the chatbot employs RAG to retrieve and process relevant documents from the knowledge base before generating a response. 
- **General Knowledge Queries:** The chatbot can also answer more general knowledge questions.
- **Dynamic Routing:** A flexible routing mechanism allows the chatbot to adapt its processing pipeline based on the type of query and other contextual factors. 
- **Response Grading:** The chatbot uses language models to assess the quality of its generated responses, checking for factual accuracy and potential hallucinations.
- **Configurable Pipeline:**  An external YAML configuration file makes it easy to customize the chatbot's behavior and routing rules without modifying the code.

### Architecture

The chatbot follows a modular pipeline structure:

1.  **Preprocessing:** The user query is cleaned and standardized.
2.  **Classification:** The query is classified into different categories (e.g., "course\_query", "general\_query"). 
3.  **Dynamic Routing:** The pipeline flow is directed based on the query classification and other criteria. 
4.  **RAG Task (Optional):** If RAG is triggered, relevant documents are retrieved, filtered, and ranked. 
5.  **Response Generation:** A language model generates a response based on the query and any relevant documents.
6.  **Response Grading:**  The generated response is evaluated for quality.

### Configuration

The pipeline's behavior and routing rules can be easily modified using an external YAML configuration file. This provides flexibility to customize the chatbot for specific use cases.

### Getting Started

*(Add instructions on how to install, configure, and run the chatbot here.)*

### Future Directions

-  Enhance the dynamic routing with more sophisticated rules and conditions.
-  Incorporate user profiles to personalize the responses. 
-  Develop an interactive learning mode, engaging users with follow-up questions and learning resources. 
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

# Study Buddy: A Modular RAG System

## Overview

Study Buddy is a Retrieval-Augmented Generation (RAG) system designed to assist students in their studies. It combines advanced natural language processing techniques with a modular architecture to provide accurate and context-aware responses to user queries.

It also demostrates that LLM inference doesn't need to be more complicated then a function or REST call by not locking itself behind a "do-it-all" framework.

## Key Features

- **Modular Architecture**: Easily extensible with well-defined interfaces for various services.
- **Local Model Support**: Utilizes local transformer models for text generation, classification, and reranking.
- **Efficient Document Retrieval**: Implements ChromaDB for fast and accurate document retrieval.
- **Query Classification**: Classifies user queries to determine the appropriate response type.
- **Document Reranking**: Improves relevance of retrieved documents through reranking.
- **Response Grading**: Evaluates generated responses for quality and relevance.
- **Configurable**: Utilizes a YAML-based configuration system for easy customization.

## System Architecture

The system is composed of several key components:

1. **RAG System**: The core class that orchestrates the entire process.
2. **Services**: 
   - Text Generation
   - Classification
   - Reranking
   - Document Retrieval
   - Text Embedding
3. **Tasks**: Modular units of work (e.g., PreprocessQuery, RetrieveDocuments, GenerateResponse)
4. **Models**: Data structures for Query, Context, Document, and Response
5. **Adapters**: Integration with external systems (e.g., ChromaDB)
6. **User Interface**: Currently implements a command-line interface

## Project Structure

```
study-buddy/
│
├── src/
│   ├── adapter/
│   │   └── chromadb.py
│   ├── interfaces/
│   │   └── services/
│   │       ├── classification.py
│   │       ├── document_retrieval.py
│   │       ├── reranking.py
│   │       ├── text_embedder.py
│   │       └── text_generation.py
│   ├── models/
│   │   ├── context.py
│   │   ├── document.py
│   │   ├── query.py
│   │   └── response.py
│   ├── service/
│   │   ├── classification/
│   │   ├── document_retrieval/
│   │   ├── reranking/
│   │   ├── text_embedder/
│   │   └── text_generation/
│   ├── tasks/
│   │   ├── utils/
│   │   ├── classify_query.py
│   │   ├── generate_response.py
│   │   ├── grade_response.py
│   │   ├── preprocess_query.py
│   │   ├── rerank_documents.py
│   │   └── retrieve_documents.py
│   ├── utils/
│   │   ├── config_manager.py
│   │   └── logging_utils.py
│   ├── view/
│   │   └── command_line_ui.py
│   └── rag_system.py
├── config/
│   └── config.yaml
├── data/
│   └── chroma/
├── main.py
└── requirements.txt
```

## Extending the System

To add new functionality:

1. Implement new services by extending the appropriate interface in `src/interfaces/services/`.
2. Create new tasks in the `src/tasks/` directory.
3. Update the `config.yaml` file to include new tasks or services.

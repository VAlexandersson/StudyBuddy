# Study-Buddy

Model: meta-llama/Meta-Llama-3-8B-Instruct

## Papers:

### Embeddings and Reranking:
[Reranking Leaderboard](https://huggingface.co/spaces/AIR-Bench/leaderboard)

[BGE M3-Embedding: Multi-Lingual, Multi-Functionality, Multi-Granularity Text Embeddings Through Self-Knowledge Distillation](https://arxiv.org/abs/2402.03216)
[Making Large Language Models A Better Foundation For Dense Retrieval](https://arxiv.org/abs/2312.15503)


## Structure:

```
study_buddy/
│
├── pipeline/
│   ├── __init__.py
│   ├── pipeline.py
│   ├── tasks/
│   │   ├── __init__.py
│   │   ├── preprocess_query.py
│   │   ├── classify_query.py
│   │   ├── decompose_query.py
│   │   ├── retrieve_documents.py
│   │   ├── filter_documents.py
│   │   ├── generate_response.py
│   │   └── grade_response.py
│
├── models/
│   ├── __init__.py
│   ├── sentence_transformer.py
│   ├── zero_shot_classifier.py
│   ├── rag.py
│   └── llm.py
│
├── utils/
│   ├── __init__.py
│   └── config.py
│
└── main.py
```

A complete rehaul of the architecture for better flexibility of the different task.


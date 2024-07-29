import pytest
import asyncio
from src.utils.config_manager import ConfigManager
from src.service.text_embedder.sentence_transformer import TextEmbedding
from src.service.text_generation.local_transformers import LocalTransformerTextGeneration
from src.service.classification.local_transformers import LocalTransformerClassification
from src.service.reranking.local_transformers import LocalTransformerReranking
from src.service.document_retrieval.chromadb import ChromaDocumentRetrievalService
from src.adapter.chromadb import ChromaDB

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def config():
    return ConfigManager()

@pytest.fixture(scope="session")
def text_embedding_service():
    return TextEmbedding(model_id="BAAI/bge-m3")

@pytest.fixture(scope="session")
def text_generation_service():
    return LocalTransformerTextGeneration(
        model_id="meta-llama/Meta-Llama-3-8B-Instruct",
        device="cuda",
        attn_implementation="sdpa"
    )

@pytest.fixture(scope="session")
def classification_service():
    return LocalTransformerClassification(
        model_id="MoritzLaurer/deberta-v3-large-zeroshot-v2.0"
    )

@pytest.fixture(scope="session")
def reranking_service():
    return LocalTransformerReranking(
        model_id='BAAI/bge-reranker-v2-m3'
    )

@pytest.fixture(scope="session")
def chromadb(text_embedding_service):
    return ChromaDB(embedding_service=text_embedding_service)

@pytest.fixture(scope="session")
def document_retrieval_service(chromadb, text_embedding_service):
    return ChromaDocumentRetrievalService(
        client=chromadb.get_client(),
        embedding_service=text_embedding_service
    )
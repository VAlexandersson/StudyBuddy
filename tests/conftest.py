import pytest
from unittest.mock import MagicMock

from src.utils.config_manager import ConfigManager
from src.interfaces.services.document_retrieval import DocumentRetrievalService
from src.interfaces.services.text_generation import TextGenerationService
from src.interfaces.services.classification import ClassificationService
from src.interfaces.services.reranking import RerankingService
from src.rag_system import RAGSystem

@pytest.fixture
def mock_config():
    config = MagicMock(spec=ConfigManager)
    config.get.side_effect = lambda key, default: {
        "TASKS": [
            {"name": "PreprocessQueryTask", "class": "src.tasks.preprocess_query.PreprocessQueryTask", "services": ["text_generation"]}
        ],
        "ROUTING": {}
    }.get(key, default)
    return config

@pytest.fixture
def mock_text_generation_service():
    return MagicMock(spec=TextGenerationService)

@pytest.fixture
def mock_classification_service():
    return MagicMock(spec=ClassificationService)

@pytest.fixture
def mock_reranking_service():
    return MagicMock(spec=RerankingService)

@pytest.fixture
def mock_document_retrieval_service():
    return MagicMock(spec=DocumentRetrievalService)

@pytest.fixture
def rag_system(mock_config, mock_text_generation_service, mock_classification_service, mock_reranking_service, mock_document_retrieval_service):
    return RAGSystem(
        config=mock_config,
        text_generation_service=mock_text_generation_service,
        classification_service=mock_classification_service,
        reranking_service=mock_reranking_service,
        document_retrieval_service=mock_document_retrieval_service
    )
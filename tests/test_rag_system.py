import pytest
from src.rag_system import RAGSystem

@pytest.fixture
def rag_system(config, text_generation_service, classification_service, reranking_service, document_retrieval_service):
    return RAGSystem(
        config=config,
        text_generation_service=text_generation_service,
        classification_service=classification_service,
        reranking_service=reranking_service,
        document_retrieval_service=document_retrieval_service
    )

@pytest.mark.asyncio
async def test_process_query(rag_system):
    query = "What is the capital of France?"
    response = await rag_system.process_query(query)
    assert isinstance(response.text, str)
    assert len(response.text) > 0
    assert "Paris" in response.text

@pytest.mark.asyncio
async def test_process_complex_query(rag_system):
    query = "Compare and contrast the nutritional value of apples and oranges."
    response = await rag_system.process_query(query)
    assert isinstance(response.text, str)
    assert len(response.text) > 0
    assert "apple" in response.text.lower()
    assert "orange" in response.text.lower()
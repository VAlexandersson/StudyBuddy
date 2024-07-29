import pytest

@pytest.mark.asyncio
async def test_generate_text(text_generation_service):
    prompt = "What is the capital of France?"
    system_prompt = "You are a helpful assistant."
    response = await text_generation_service.generate_text(prompt, system_prompt)
    assert isinstance(response, str)
    assert len(response) > 0
    assert "Paris" in response


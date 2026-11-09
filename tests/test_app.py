import json

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app import ChatResponse, app

client = TestClient(app)


def test_chat_returns_structured_json():
    response = client.post("/chat", json={"prompt": "Merhaba"})

    assert response.status_code == 200
    assert ChatResponse.model_validate(response.json()).answer == "Mock yanıt: Merhaba"


@pytest.mark.parametrize("prompt", ["", " " * 501])
def test_chat_rejects_invalid_prompt(prompt: str):
    response = client.post("/chat", json={"prompt": prompt})

    assert response.status_code == 422


def test_response_schema_rejects_out_of_range_confidence():
    with pytest.raises(ValidationError):
        ChatResponse(answer="Yanıt", confidence=1.5)


def test_stream_emits_chunks_and_completion_marker():
    response = client.post("/chat/stream", json={"prompt": "Merhaba"})

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    chunks = [
        json.loads(line.removeprefix("data: "))["chunk"]
        for line in response.text.splitlines()
        if line.startswith("data: {")
    ]
    assert "".join(chunks) == "Mock yanıt: Merhaba"
    assert "data: [DONE]" in response.text

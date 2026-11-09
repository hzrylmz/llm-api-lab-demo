import json
from collections.abc import Iterator

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

app = FastAPI(title="LLM API Lab")


class ChatRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=500)


class ChatResponse(BaseModel):
    answer: str
    confidence: float = Field(ge=0, le=1)


def make_answer(prompt: str) -> ChatResponse:
    return ChatResponse(answer=f"Mock yanıt: {prompt}", confidence=0.99)


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    return make_answer(request.prompt)


def answer_chunks(answer: str, chunk_size: int = 12) -> Iterator[str]:
    for start in range(0, len(answer), chunk_size):
        yield answer[start : start + chunk_size]


@app.post("/chat/stream")
def chat_stream(request: ChatRequest) -> StreamingResponse:
    answer = make_answer(request.prompt).answer

    def events() -> Iterator[str]:
        for chunk in answer_chunks(answer):
            payload = json.dumps({"chunk": chunk}, ensure_ascii=False)
            yield f"data: {payload}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(events(), media_type="text/event-stream")

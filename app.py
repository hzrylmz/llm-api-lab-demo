import json
from collections.abc import Iterator

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

app = FastAPI(title="LLM API Lab")

MOCK_ANSWERS = {
    "Fransa'nın başkenti neresi?": "Paris",
    "Türkiye'nin başkenti neresi?": "Ankara",
    "2 + 2 kaçtır?": "4",
    "3 x 3 kaçtır?": "9",
    "JSON bir veri formatı mıdır?": "Evet",
    "HTTP 404 ne anlama gelir?": "Kaynak bulunamadı",
    "HTTP 200 ne anlama gelir?": "Başarılı",
    "Python'da liste hangi parantezle yazılır?": "[]",
}


class ChatRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=500)


class ChatResponse(BaseModel):
    answer: str
    confidence: float = Field(ge=0, le=1)


def make_answer(prompt: str) -> ChatResponse:
    answer = MOCK_ANSWERS.get(prompt, f"Mock yanıt: {prompt}")
    return ChatResponse(answer=answer, confidence=0.99)


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

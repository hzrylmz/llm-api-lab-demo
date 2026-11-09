import json
from collections.abc import Iterator

import httpx

from app import ChatResponse


def ask(base_url: str, prompt: str) -> ChatResponse:
    response = httpx.post(
        f"{base_url.rstrip('/')}/chat",
        json={"prompt": prompt},
        timeout=10,
    )
    response.raise_for_status()
    return ChatResponse.model_validate(response.json())


def stream_answer(base_url: str, prompt: str) -> Iterator[str]:
    with httpx.stream(
        "POST",
        f"{base_url.rstrip('/')}/chat/stream",
        json={"prompt": prompt},
        timeout=10,
    ) as response:
        response.raise_for_status()
        for line in response.iter_lines():
            if not line.startswith("data: "):
                continue
            payload = line.removeprefix("data: ")
            if payload == "[DONE]":
                return
            yield json.loads(payload)["chunk"]


if __name__ == "__main__":
    url = "http://127.0.0.1:8000"
    print("Normal yanıt:", ask(url, "REST ve JSON nedir?").model_dump())
    print("Streaming yanıt: ", end="", flush=True)
    for part in stream_answer(url, "Streaming yanıtı parça parça verir."):
        print(part, end="", flush=True)
    print()

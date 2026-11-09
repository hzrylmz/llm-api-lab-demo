# LLM API Lab

Küçük, anahtarsız bir demo: yerel bir mock API ile REST, JSON, Pydantic
structured output ve SSE streaming kavramlarını denemek.

## Kurulum ve çalıştırma

Python 3.11+ gerekir.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
uvicorn app:app --reload
```

Servis `http://127.0.0.1:8000` adresinde çalışır. `http://127.0.0.1:8000/docs`
adresinden endpoint'leri tarayıcıda deneyebilirsin. Başka bir terminalde:

```bash
python client.py
```

## Öğrenme deneyi

1. `POST /chat` adresine `{"prompt": "Merhaba"}` JSON gövdesi gönder.
2. Yanıttaki `answer` ve `confidence` alanlarını incele. Bunlar Pydantic
   `ChatResponse` şemasına uymalı.
3. Boş veya 500 karakterden uzun prompt gönder; API `422` ile reddeder.
4. `POST /chat/stream` çağrısında SSE `data:` olaylarını izle. Yanıt JSON
   chunk'ları halinde gelir ve `[DONE]` olayıyla biter.
5. Kodu değiştirip testleri çalıştır: `pytest -q`.

## Dosyalar

- `app.py`: FastAPI mock servisi ve Pydantic veri modelleri.
- `client.py`: HTTPX ile REST isteği ve SSE stream okuyucusu.
- `tests/test_app.py`: başarılı yanıt, doğrulama ve streaming testleri.

Bu servis gerçek bir dil modeli çağırmaz; amaç API ve test akışını dış
servis, API anahtarı veya ücret olmadan öğrenmektir.

# LLM API Lab

A local learning demo for REST, JSON, Pydantic validation, SSE streaming,
and dataset-based evaluation. No real LLM, API key, or paid service required.

## Run

Requires Python 3.11+.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
python -m uvicorn app:app --reload
```

Open [Swagger UI](http://127.0.0.1:8000/docs):
`POST /chat` returns structured JSON; `POST /chat/stream` returns SSE events.
Both accept `{"prompt": "Merhaba"}`.

## Evaluate

With the API running, activate the same environment in another terminal:

```bash
source .venv/bin/activate
python client.py
python -m evaluate
```

The 10-case dataset initially scores **80%**, with two intentional failures.
Results are saved to `evaluation-report.json`. The default 100% quality gate
returns exit code `1`; use `--min-accuracy 0.8` to pass at 80%.

Scoring uses exact text equality, not semantic evaluation. The mock
`confidence` is a fixed example value, not measured confidence.

## Test

```bash
python -m pytest -v
```

Tests use `TestClient` and do not require a running server. If your existing
environment is named `.venv-1`, use that activation path instead of `.venv`.

See [the Turkish project walkthrough](PROJE_OZETI.md) for diagrams and explanations.

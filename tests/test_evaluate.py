import json
from pathlib import Path

import httpx
import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app import app
from evaluate import load_dataset, main, run_evaluation

DATASET = Path(__file__).resolve().parents[1] / "datasets" / "questions.json"


def test_demo_dataset_produces_eight_passes_and_two_failures():
    with TestClient(app) as client:
        report = run_evaluation(load_dataset(DATASET), client)

    assert (report.total, report.passed, report.failed, report.accuracy) == (10, 8, 2, 0.8)
    assert [result.id for result in report.results if not result.passed] == [
        "capital-de",
        "subtraction",
    ]


@pytest.mark.parametrize(
    "data",
    [
        [],
        [{"id": "missing-fields"}],
        [{"id": "a", "prompt": "", "expected_answer": "x"}],
        [{"id": "a", "prompt": "q", "expected_answer": 1}],
        [{"id": "a", "prompt": "q", "expected_answer": "x"}] * 2,
    ],
)
def test_invalid_dataset_is_rejected(tmp_path, data):
    path = tmp_path / "dataset.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError):
        load_dataset(path)


@pytest.mark.parametrize(
    ("status", "body", "error"),
    [(500, {"detail": "Server error"}, httpx.HTTPStatusError),
     (200, {"answer": "Paris", "confidence": 2}, ValidationError)],
)
def test_api_errors_are_not_reported_as_answer_mismatches(status, body, error):
    transport = httpx.MockTransport(
        lambda request: httpx.Response(status, json=body)
    )
    with httpx.Client(transport=transport, base_url="http://test") as client:
        with pytest.raises(error):
            run_evaluation(load_dataset(DATASET), client)


@pytest.mark.parametrize(("threshold", "exit_code"), [("1", 1), ("0.8", 0)])
def test_cli_saves_report_and_sets_exit_code(tmp_path, monkeypatch, threshold, exit_code):
    report_path = tmp_path / "report.json"
    monkeypatch.setattr(
        "sys.argv",
        ["evaluate", "--dataset", str(DATASET), "--report", str(report_path),
         "--min-accuracy", threshold],
    )
    monkeypatch.setattr("evaluate.httpx.Client", lambda **kwargs: TestClient(app))

    assert main() == exit_code
    assert json.loads(report_path.read_text(encoding="utf-8"))["accuracy"] == 0.8

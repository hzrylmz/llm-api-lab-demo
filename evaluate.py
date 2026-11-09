import argparse
import json
from pathlib import Path

import httpx
from pydantic import BaseModel, ConfigDict, Field, TypeAdapter

from app import ChatResponse


class EvaluationCase(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    id: str = Field(min_length=1)
    prompt: str = Field(min_length=1, max_length=500)
    expected_answer: str = Field(min_length=1)


class CaseResult(BaseModel):
    id: str
    prompt: str
    expected_answer: str
    actual_answer: str
    passed: bool


class EvaluationReport(BaseModel):
    total: int
    passed: int
    failed: int
    accuracy: float
    results: list[CaseResult]


def load_dataset(path: Path) -> list[EvaluationCase]:
    cases = TypeAdapter(list[EvaluationCase]).validate_json(
        path.read_text(encoding="utf-8")
    )
    if not cases:
        raise ValueError("Dataset en az bir senaryo içermeli.")
    if len({case.id for case in cases}) != len(cases):
        raise ValueError("Dataset içindeki senaryo ID'leri benzersiz olmalı.")
    return cases


def run_evaluation(
    cases: list[EvaluationCase], client: httpx.Client
) -> EvaluationReport:
    if not cases:
        raise ValueError("Değerlendirme en az bir senaryo gerektirir.")
    results = []
    for case in cases:
        response = client.post("/chat", json={"prompt": case.prompt})
        response.raise_for_status()
        answer = ChatResponse.model_validate(response.json()).answer
        results.append(
            CaseResult(
                id=case.id,
                prompt=case.prompt,
                expected_answer=case.expected_answer,
                actual_answer=answer,
                passed=answer == case.expected_answer,
            )
        )
    passed = sum(result.passed for result in results)
    return EvaluationReport(
        total=len(results),
        passed=passed,
        failed=len(results) - passed,
        accuracy=passed / len(results),
        results=results,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Mock API için exact-match evaluation")
    parser.add_argument("--dataset", type=Path, default=Path("datasets/questions.json"))
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--report", type=Path, default=Path("evaluation-report.json"))
    parser.add_argument("--min-accuracy", type=float, default=1.0)
    args = parser.parse_args()
    if not 0 <= args.min_accuracy <= 1:
        parser.error("--min-accuracy 0 ile 1 arasında olmalı.")
    cases = load_dataset(args.dataset)
    with httpx.Client(base_url=args.base_url, timeout=10) as client:
        report = run_evaluation(cases, client)
    args.report.write_text(
        json.dumps(report.model_dump(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Toplam senaryo: {report.total}")
    print(f"Başarılı: {report.passed}")
    print(f"Başarısız: {report.failed}")
    print(f"Doğruluk: %{report.accuracy * 100:.0f}")
    for result in report.results:
        if not result.passed:
            print(
                f"FAIL [{result.id}] Beklenen: {result.expected_answer!r}"
                f" | Gerçek: {result.actual_answer!r}"
            )
    gate_passed = report.accuracy >= args.min_accuracy
    print(f"Kalite kapısı: {'PASS' if gate_passed else 'FAIL'}")
    print(f"Rapor: {args.report}")
    return 0 if gate_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

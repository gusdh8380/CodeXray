from __future__ import annotations

import json

from codexray.summary import to_json
from codexray.summary.types import Action, Strength, SummaryResult, Weakness


def _result() -> SummaryResult:
    return SummaryResult(
        schema_version=1,
        strengths=(
            Strength(
                category="quality",
                text="coupling 차원 A 등급",
                evidence={"dimension": "coupling", "grade": "A", "score": 90},
            ),
        ),
        weaknesses=(
            Weakness(
                category="quality",
                text="test 차원 F 등급",
                evidence={"dimension": "test", "grade": "F", "score": 10},
            ),
        ),
        actions=(
            Action(
                text="characterization test 우선 보강",
                evidence={"dimension": "test", "grade": "F", "score": 10},
            ),
        ),
    )


def test_schema_version_in_payload() -> None:
    payload = json.loads(to_json(_result()))
    assert payload["schema_version"] == 1


def test_byte_determinism() -> None:
    a = to_json(_result())
    b = to_json(_result())
    assert a == b
    # 다른 dict insertion 순서로 만든 evidence 도 같은 byte.
    other = SummaryResult(
        schema_version=1,
        strengths=(
            Strength(
                category="quality",
                text="coupling 차원 A 등급",
                evidence={"score": 90, "grade": "A", "dimension": "coupling"},
            ),
        ),
        weaknesses=(),
        actions=(),
    )
    assert to_json(other) == to_json(
        SummaryResult(
            schema_version=1,
            strengths=(
                Strength(
                    category="quality",
                    text="coupling 차원 A 등급",
                    evidence={"dimension": "coupling", "grade": "A", "score": 90},
                ),
            ),
            weaknesses=(),
            actions=(),
        )
    )


def test_keys_sorted_in_output() -> None:
    output = to_json(_result())
    payload = json.loads(output)
    # Top-level keys alphabetical (json.dumps sort_keys=True).
    keys = list(payload.keys())
    assert keys == sorted(keys)


def test_evidence_includes_required_fields() -> None:
    payload = json.loads(to_json(_result()))
    assert payload["strengths"][0]["evidence"]["dimension"] == "coupling"
    assert payload["weaknesses"][0]["evidence"]["grade"] == "F"
    assert payload["actions"][0]["evidence"]["score"] == 10

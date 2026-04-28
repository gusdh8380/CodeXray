from __future__ import annotations

from pathlib import Path

from ..language import classify
from ..loc import count_nonempty_lines
from ..walk import walk
from .scoring import score_to_grade
from .types import DimensionScore

_TEST_DIR_NAMES = frozenset({"tests", "test", "__tests__"})


def _is_test_file(rel: Path) -> bool:
    parts = rel.parts
    for i, part in enumerate(parts):
        if part in _TEST_DIR_NAMES:
            return True
        if part == "Tests" and i >= 1 and parts[i - 1] == "Assets":
            return True
        if (
            part == "Tests"
            and i >= 2
            and parts[i - 1] == "Scripts"
            and parts[i - 2] == "Assets"
        ):
            return True
    name = rel.name
    if name.startswith("test_") and name.endswith(".py"):
        return True
    if name.endswith("_test.py"):
        return True
    if name.endswith((".test.ts", ".test.js", ".spec.ts", ".spec.js")):
        return True
    return name.endswith(("Tests.cs", "Test.cs"))


def compute(root: Path) -> DimensionScore:
    root = root.resolve()
    src_loc = 0
    test_loc = 0
    for path in walk(root):
        if classify(path) is None:
            continue
        rel = path.relative_to(root)
        loc = count_nonempty_lines(path)
        if _is_test_file(rel):
            test_loc += loc
        else:
            src_loc += loc

    if src_loc == 0:
        return DimensionScore(
            score=None, grade=None, detail={"reason": "no source LoC"}
        )

    ratio = test_loc / src_loc
    score = min(100, round(ratio * 200))
    return DimensionScore(
        score=score,
        grade=score_to_grade(score),
        detail={"src_loc": src_loc, "test_loc": test_loc, "ratio": round(ratio, 2)},
    )

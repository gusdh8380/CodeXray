from __future__ import annotations

import ast
import re
from pathlib import Path

from ..language import classify
from ..walk import walk
from .scoring import score_to_grade
from .types import DimensionScore

_CSHARP_TYPE_DECL = re.compile(
    r"^\s*(?:(?:public|internal|private|protected|sealed|static|abstract|partial)\s+)+"
    r"(?:class|interface|struct|record|enum)\s+\w+",
)
_CSHARP_METHOD_DECL = re.compile(
    r"^\s*(?:public|internal|protected)\s+"
    r"(?:(?:static|async|override|virtual|abstract|partial|sealed|readonly)\s+)*"
    r"[A-Za-z_]\w*(?:<[^>]+>)?\s+\w+\s*\(",
)


def compute(root: Path) -> DimensionScore:
    documented = 0
    total = 0
    for path in walk(root):
        language = classify(path)
        if language not in ("Python", "C#"):
            continue
        try:
            source = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if language == "Python":
            d, t = _python_doc_count(source)
        else:
            d, t = _csharp_doc_count(source)
        documented += d
        total += t

    if total == 0:
        return DimensionScore(
            score=None,
            grade=None,
            detail={"reason": "no Python or C# items found"},
        )

    score = round(documented / total * 100)
    return DimensionScore(
        score=score,
        grade=score_to_grade(score),
        detail={"items_total": total, "documented": documented},
    )


def _python_doc_count(source: str) -> tuple[int, int]:
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return 0, 0
    items: list[ast.AST] = [tree]
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef):
            items.append(node)
    documented = sum(1 for item in items if _has_python_docstring(item))
    return documented, len(items)


def _has_python_docstring(item: ast.AST) -> bool:
    body = getattr(item, "body", None)
    if not body:
        return False
    first = body[0]
    return (
        isinstance(first, ast.Expr)
        and isinstance(first.value, ast.Constant)
        and isinstance(first.value.value, str)
    )


def _csharp_doc_count(source: str) -> tuple[int, int]:
    lines = source.splitlines()
    documented = 0
    total = 0
    for i, line in enumerate(lines):
        if not (_CSHARP_TYPE_DECL.match(line) or _CSHARP_METHOD_DECL.match(line)):
            continue
        total += 1
        j = i - 1
        while j >= 0 and lines[j].strip() == "":
            j -= 1
        if j >= 0 and lines[j].lstrip().startswith("///"):
            documented += 1
    return documented, total

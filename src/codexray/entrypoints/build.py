from __future__ import annotations

from pathlib import Path

from ..language import classify
from ..walk import walk
from .csharp_detector import detect_main_method
from .manifest_detector import detect_package_json, detect_pyproject
from .python_detector import detect_main_guard
from .types import Entrypoint, EntrypointResult
from .unity_detector import detect_unity_lifecycle

SCHEMA_VERSION = 1


def build_entrypoints(root: Path) -> EntrypointResult:
    root = root.resolve()
    out: list[Entrypoint] = []

    out.extend(detect_pyproject(root))
    out.extend(detect_package_json(root))

    for path in walk(root):
        language = classify(path)
        if language not in ("Python", "C#"):
            continue
        try:
            source = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        rel = path.relative_to(root).as_posix()

        if language == "Python":
            if detect_main_guard(source):
                out.append(
                    Entrypoint(
                        path=rel, language="Python", kind="main_guard", detail=""
                    )
                )
        elif language == "C#":
            return_type = detect_main_method(source)
            if return_type is not None:
                out.append(
                    Entrypoint(
                        path=rel, language="C#", kind="main_method", detail=return_type
                    )
                )
            lifecycle = detect_unity_lifecycle(source)
            if lifecycle:
                out.append(
                    Entrypoint(
                        path=rel,
                        language="C#",
                        kind="unity_lifecycle",
                        detail=", ".join(lifecycle),
                    )
                )

    out.sort(key=lambda e: (e.path, e.kind, e.detail))
    return EntrypointResult(schema_version=SCHEMA_VERSION, entrypoints=tuple(out))

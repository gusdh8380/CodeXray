from __future__ import annotations

import json
import sys
import tomllib
from pathlib import Path

from .types import Entrypoint


def detect_pyproject(root: Path) -> list[Entrypoint]:
    path = root / "pyproject.toml"
    if not path.is_file():
        return []
    try:
        with path.open("rb") as fh:
            data = tomllib.load(fh)
    except (OSError, tomllib.TOMLDecodeError) as exc:
        print(f"warning: failed to parse pyproject.toml: {exc}", file=sys.stderr)
        return []
    scripts = (data.get("project") or {}).get("scripts") or {}
    if not isinstance(scripts, dict):
        return []
    return [
        Entrypoint(
            path="pyproject.toml",
            language=None,
            kind="pyproject_script",
            detail=str(name),
        )
        for name in scripts
    ]


def detect_package_json(root: Path) -> list[Entrypoint]:
    path = root / "package.json"
    if not path.is_file():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"warning: failed to parse package.json: {exc}", file=sys.stderr)
        return []
    if not isinstance(data, dict):
        return []

    out: list[Entrypoint] = []
    bin_field = data.get("bin")
    if isinstance(bin_field, str):
        out.append(
            Entrypoint(
                path="package.json",
                language=None,
                kind="package_bin",
                detail=bin_field,
            )
        )
    elif isinstance(bin_field, dict):
        for name in bin_field:
            out.append(
                Entrypoint(
                    path="package.json",
                    language=None,
                    kind="package_bin",
                    detail=str(name),
                )
            )

    main_field = data.get("main")
    if isinstance(main_field, str):
        out.append(
            Entrypoint(
                path="package.json",
                language=None,
                kind="package_main",
                detail=main_field,
            )
        )

    scripts = data.get("scripts")
    if isinstance(scripts, dict):
        for name in scripts:
            out.append(
                Entrypoint(
                    path="package.json",
                    language=None,
                    kind="package_script",
                    detail=str(name),
                )
            )
    return out

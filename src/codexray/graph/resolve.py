from __future__ import annotations

from pathlib import Path

from .types import RawImport

_JS_EXT_CANDIDATES: tuple[str, ...] = (".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs")


def resolve(raw: RawImport, root: Path, internal_paths: set[Path]) -> Path | None:
    if raw.language == "Python":
        return _resolve_python(raw, root, internal_paths)
    return _resolve_js(raw, internal_paths)


def _resolve_python(raw: RawImport, root: Path, internal_paths: set[Path]) -> Path | None:
    parts = [p for p in raw.raw.split(".") if p]
    if raw.level == 0:
        if not parts:
            return None
        bases = [root, root / "src"]
        for base in bases:
            candidate = base.joinpath(*parts).with_suffix(".py")
            if candidate in internal_paths:
                return candidate
            init_candidate = base.joinpath(*parts) / "__init__.py"
            if init_candidate in internal_paths:
                return init_candidate
        return None

    anchor = raw.source.parent
    for _ in range(raw.level - 1):
        anchor = anchor.parent
    if not parts:
        candidate = anchor / "__init__.py"
        return candidate if candidate in internal_paths else None
    candidate = anchor.joinpath(*parts).with_suffix(".py")
    if candidate in internal_paths:
        return candidate
    init_candidate = anchor.joinpath(*parts) / "__init__.py"
    if init_candidate in internal_paths:
        return init_candidate
    return None


def _resolve_js(raw: RawImport, internal_paths: set[Path]) -> Path | None:
    spec = raw.raw
    if not (spec.startswith("./") or spec.startswith("../")):
        return None
    base = (raw.source.parent / spec).resolve(strict=False)
    if base in internal_paths:
        return base
    if not base.suffix:
        for ext in _JS_EXT_CANDIDATES:
            candidate = base.with_name(base.name + ext)
            if candidate in internal_paths:
                return candidate
    for ext in _JS_EXT_CANDIDATES:
        candidate = base / f"index{ext}"
        if candidate in internal_paths:
            return candidate
    return None

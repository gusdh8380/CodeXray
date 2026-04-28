from __future__ import annotations

from pathlib import Path

from .types import RawImport

_JS_EXT_CANDIDATES: tuple[str, ...] = (".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs")


def resolve_python(raw: RawImport, root: Path, internal_paths: set[Path]) -> list[Path]:
    parts = [p for p in raw.raw.split(".") if p]
    if raw.level == 0:
        if not parts:
            return []
        for base in (root, root / "src"):
            candidate = base.joinpath(*parts).with_suffix(".py")
            if candidate in internal_paths:
                return [candidate]
            init_candidate = base.joinpath(*parts) / "__init__.py"
            if init_candidate in internal_paths:
                return [init_candidate]
        return []

    anchor = raw.source.parent
    for _ in range(raw.level - 1):
        anchor = anchor.parent
    if not parts:
        candidate = anchor / "__init__.py"
        return [candidate] if candidate in internal_paths else []
    candidate = anchor.joinpath(*parts).with_suffix(".py")
    if candidate in internal_paths:
        return [candidate]
    init_candidate = anchor.joinpath(*parts) / "__init__.py"
    if init_candidate in internal_paths:
        return [init_candidate]
    return []


def resolve_js(raw: RawImport, internal_paths: set[Path]) -> list[Path]:
    spec = raw.raw
    if not (spec.startswith("./") or spec.startswith("../")):
        return []
    base = (raw.source.parent / spec).resolve(strict=False)
    if base in internal_paths:
        return [base]
    if not base.suffix:
        for ext in _JS_EXT_CANDIDATES:
            candidate = base.with_name(base.name + ext)
            if candidate in internal_paths:
                return [candidate]
    for ext in _JS_EXT_CANDIDATES:
        candidate = base / f"index{ext}"
        if candidate in internal_paths:
            return [candidate]
    return []


def resolve_csharp_types(
    namespace: str,
    source_file: Path,
    type_usages: set[str],
    type_index: dict[tuple[str, str], Path],
) -> list[Path]:
    """Return internal files where any used type is declared inside ``namespace``."""
    matched: set[Path] = set()
    for type_name in type_usages:
        target = type_index.get((namespace, type_name))
        if target is not None and target != source_file:
            matched.add(target)
    return sorted(matched)


def resolve(
    raw: RawImport,
    root: Path,
    internal_paths: set[Path],
    namespace_index: dict[str, set[Path]] | None = None,
) -> list[Path]:
    """Backward-compatible single-entry resolver retained for tests.

    For C#, this performs the legacy 1:N namespace-only matching and ignores
    type-resolution. The build pipeline calls language-specific resolvers
    directly with the richer indexes.
    """
    if raw.language == "Python":
        return resolve_python(raw, root, internal_paths)
    if raw.language == "C#":
        files = (namespace_index or {}).get(raw.raw, set())
        return sorted(files)
    return resolve_js(raw, internal_paths)

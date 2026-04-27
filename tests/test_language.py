from pathlib import Path

from codexray.language import classify


def test_mapped_extensions() -> None:
    assert classify(Path("a/b/main.py")) == "Python"
    assert classify(Path("index.ts")) == "TypeScript"
    assert classify(Path("App.tsx")) == "TypeScript"
    assert classify(Path("svc.cs")) == "C#"
    assert classify(Path("App.java")) == "Java"
    assert classify(Path("a.cjs")) == "JavaScript"


def test_unmapped_extension_returns_none() -> None:
    assert classify(Path("README.md")) is None
    assert classify(Path("data.json")) is None
    assert classify(Path("logo.png")) is None
    assert classify(Path("Dockerfile")) is None


def test_case_insensitive_extension() -> None:
    assert classify(Path("Main.PY")) == "Python"
    assert classify(Path("Index.TS")) == "TypeScript"

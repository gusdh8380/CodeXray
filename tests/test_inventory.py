from pathlib import Path

from codexray.inventory import aggregate


def _make(tmp_path: Path, name: str, content: str) -> None:
    p = tmp_path / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)


def test_multi_language_sorted_by_loc(tmp_path: Path) -> None:
    _make(tmp_path, "a.py", "x=1\n" * 100)
    _make(tmp_path, "b.py", "y=2\n" * 100)
    _make(tmp_path, "c.py", "")
    _make(tmp_path, "d.ts", "let z=3;\n" * 50)

    rows = aggregate(tmp_path)
    languages = [r.language for r in rows]
    assert languages == ["Python", "TypeScript"]
    py = next(r for r in rows if r.language == "Python")
    ts = next(r for r in rows if r.language == "TypeScript")
    assert py.file_count == 3
    assert py.loc == 200
    assert ts.file_count == 1
    assert ts.loc == 50


def test_skips_unknown_extensions(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("# hi\n")
    (tmp_path / "data.json").write_text('{"a":1}\n')
    (tmp_path / "logo.png").write_bytes(b"\x89PNG\r\n")

    assert aggregate(tmp_path) == []


def test_loc_excludes_blank_lines(tmp_path: Path) -> None:
    (tmp_path / "a.py").write_text("x=1\n\nprint(1)\n\n\n\n\n")
    rows = aggregate(tmp_path)
    assert len(rows) == 1
    assert rows[0].loc == 2

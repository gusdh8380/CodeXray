from pathlib import Path

from codexray.loc import count_nonempty_lines


def test_empty_file(tmp_path: Path) -> None:
    f = tmp_path / "a.py"
    f.write_text("")
    assert count_nonempty_lines(f) == 0


def test_skips_blank_lines(tmp_path: Path) -> None:
    f = tmp_path / "a.py"
    f.write_text("import x\n\nprint(1)\n\n\n")
    assert count_nonempty_lines(f) == 2


def test_skips_whitespace_only_lines(tmp_path: Path) -> None:
    f = tmp_path / "a.py"
    f.write_text("import x\n   \n\t\nprint(1)\n")
    assert count_nonempty_lines(f) == 2


def test_handles_non_utf8_bytes(tmp_path: Path) -> None:
    f = tmp_path / "a.py"
    f.write_bytes(b"x = 1\n\xff\xfeinvalid\n\n")
    assert count_nonempty_lines(f) == 2

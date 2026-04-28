from pathlib import Path

from codexray.entrypoints.manifest_detector import (
    detect_package_json,
    detect_pyproject,
)


def test_pyproject_scripts(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname="x"\n[project.scripts]\nfoo = "x.cli:app"\nbar = "x.cli:bar"\n'
    )
    eps = detect_pyproject(tmp_path)
    details = sorted(e.detail for e in eps)
    assert details == ["bar", "foo"]
    assert all(e.kind == "pyproject_script" for e in eps)
    assert all(e.path == "pyproject.toml" for e in eps)
    assert all(e.language is None for e in eps)


def test_pyproject_missing(tmp_path: Path) -> None:
    assert detect_pyproject(tmp_path) == []


def test_pyproject_invalid(tmp_path: Path, capsys) -> None:
    (tmp_path / "pyproject.toml").write_text("not = valid = toml = !!\n")
    assert detect_pyproject(tmp_path) == []
    err = capsys.readouterr().err
    assert "pyproject" in err


def test_package_json_bin_string(tmp_path: Path) -> None:
    (tmp_path / "package.json").write_text('{"bin": "./bin/cli.js"}')
    eps = detect_package_json(tmp_path)
    assert len(eps) == 1
    assert eps[0].kind == "package_bin"
    assert eps[0].detail == "./bin/cli.js"


def test_package_json_bin_dict(tmp_path: Path) -> None:
    (tmp_path / "package.json").write_text(
        '{"bin": {"foo": "./foo.js", "bar": "./bar.js"}}'
    )
    eps = detect_package_json(tmp_path)
    details = sorted(e.detail for e in eps)
    assert details == ["bar", "foo"]
    assert all(e.kind == "package_bin" for e in eps)


def test_package_json_main(tmp_path: Path) -> None:
    (tmp_path / "package.json").write_text('{"main": "dist/index.js"}')
    eps = detect_package_json(tmp_path)
    assert eps == [eps[0]]
    assert eps[0].kind == "package_main"
    assert eps[0].detail == "dist/index.js"


def test_package_json_scripts(tmp_path: Path) -> None:
    (tmp_path / "package.json").write_text(
        '{"scripts": {"build": "tsc", "test": "vitest"}}'
    )
    eps = detect_package_json(tmp_path)
    details = sorted(e.detail for e in eps)
    assert details == ["build", "test"]
    assert all(e.kind == "package_script" for e in eps)


def test_package_json_invalid(tmp_path: Path, capsys) -> None:
    (tmp_path / "package.json").write_text("not json {")
    assert detect_package_json(tmp_path) == []
    err = capsys.readouterr().err
    assert "package.json" in err

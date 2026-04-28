from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient
from typer.testing import CliRunner

import codexray.cli as cli
import codexray.web.routes as routes
from codexray.web import create_app
from codexray.web.jobs import ReviewJob


def _make_tree(root: Path) -> None:
    (root / "a.py").write_text("from .b import value\n")
    (root / "b.py").write_text("value = 1\n")
    (root / "README.md").write_text("# example\n")


def test_main_page_contains_path_and_tabs() -> None:
    client = TestClient(create_app())
    response = client.get("/")
    assert response.status_code == 200
    assert 'id="path-input"' in response.text
    assert 'id="result-panel"' in response.text
    assert 'hx-post="/api/inventory"' in response.text
    assert "https://unpkg.com/htmx.org" in response.text


def test_path_validation_rejects_missing_path(tmp_path: Path) -> None:
    client = TestClient(create_app())
    response = client.post("/api/inventory", data={"path": str(tmp_path / "missing")})
    assert response.status_code == 400
    assert "path does not exist" in response.text


def test_path_validation_rejects_file_path(tmp_path: Path) -> None:
    file_path = tmp_path / "file.py"
    file_path.write_text("x = 1\n")
    client = TestClient(create_app())
    response = client.post("/api/inventory", data={"path": str(file_path)})
    assert response.status_code == 400
    assert "path is not a directory" in response.text


def test_deterministic_endpoints_return_fragments(tmp_path: Path) -> None:
    _make_tree(tmp_path)
    client = TestClient(create_app())
    endpoints = [
        "/api/overview",
        "/api/inventory",
        "/api/graph",
        "/api/metrics",
        "/api/entrypoints",
        "/api/quality",
        "/api/hotspots",
        "/api/report",
    ]
    for endpoint in endpoints:
        response = client.post(endpoint, data={"path": str(tmp_path)})
        assert response.status_code == 200, endpoint
        assert 'data-codexray-result="' in response.text


def test_dashboard_endpoint_returns_iframe(tmp_path: Path) -> None:
    _make_tree(tmp_path)
    client = TestClient(create_app())
    response = client.post("/api/dashboard", data={"path": str(tmp_path)})
    assert response.status_code == 200
    assert "dashboard-frame" in response.text
    assert "codexray-dashboard-v1" in response.text


def test_review_endpoint_is_opt_in(tmp_path: Path) -> None:
    _make_tree(tmp_path)
    client = TestClient(create_app())
    response = client.post("/api/review", data={"path": str(tmp_path)})
    assert response.status_code == 200
    assert "AI review is opt-in" in response.text
    assert "1-5 minutes" in response.text
    assert 'name="run" value="true"' in response.text


def test_review_run_starts_background_job(tmp_path: Path, monkeypatch) -> None:
    _make_tree(tmp_path)
    calls: list[Path] = []

    def fake_start(root: Path) -> ReviewJob:
        calls.append(root)
        return ReviewJob(id="job123", root=root, status="running")

    monkeypatch.setattr(routes, "start_review_job", fake_start)
    client = TestClient(create_app())
    response = client.post("/api/review", data={"path": str(tmp_path), "run": "true"})
    assert response.status_code == 200
    assert calls == [tmp_path.resolve()]
    assert "AI review is running" in response.text
    assert 'hx-get="/api/review/status/job123"' in response.text


def test_review_status_unknown_job_returns_error() -> None:
    client = TestClient(create_app())
    response = client.get("/api/review/status/unknown")
    assert response.status_code == 400
    assert "review job not found" in response.text


def test_cli_serve_wires_options(monkeypatch) -> None:
    calls: list[tuple[str, int, bool]] = []

    def fake_serve(host: str, port: int, open_browser: bool) -> None:
        calls.append((host, port, open_browser))

    monkeypatch.setattr(cli, "serve_web", fake_serve)
    result = CliRunner().invoke(
        cli.app,
        ["serve", "--host", "127.0.0.1", "--port", "8090", "--no-browser"],
    )
    assert result.exit_code == 0, result.output
    assert calls == [("127.0.0.1", 8090, False)]

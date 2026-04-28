from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient
from typer.testing import CliRunner

import codexray.cli as cli
import codexray.web.routes as routes
from codexray.web import create_app
from codexray.web.folder_picker import FolderPickerResult
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
    assert 'id="status-text"' in response.text
    assert 'id="theme-toggle"' in response.text
    assert 'hx-post="/api/browse-folder"' in response.text
    assert 'id="result-panel"' in response.text
    assert 'class="tab-button is-active"' in response.text
    assert 'hx-post="/api/inventory"' in response.text
    assert 'hx-post="/api/vibe-coding"' in response.text
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
        "/api/vibe-coding",
    ]
    for endpoint in endpoints:
        response = client.post(endpoint, data={"path": str(tmp_path)})
        assert response.status_code == 200, endpoint
        assert 'data-codexray-result="' in response.text
        assert (
            "Raw JSON" in response.text
            or endpoint in {"/api/overview", "/api/report"}
        )
        assert "json-output" not in response.text or "Raw JSON" in response.text


def test_analysis_panels_include_korean_explainer(tmp_path: Path) -> None:
    _make_tree(tmp_path)
    client = TestClient(create_app())
    endpoints = [
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
        assert "analysis-explainer" in response.text
        assert "시니어 개발자 관점" in response.text


def test_dashboard_endpoint_returns_iframe(tmp_path: Path) -> None:
    _make_tree(tmp_path)
    client = TestClient(create_app())
    response = client.post("/api/dashboard", data={"path": str(tmp_path)})
    assert response.status_code == 200
    assert "dashboard-frame" in response.text
    assert "dashboard-workspace" in response.text
    assert "codexray-dashboard-v1" in response.text


def test_vibe_coding_endpoint_renders_non_developer_report(tmp_path: Path) -> None:
    _make_tree(tmp_path)
    (tmp_path / "AGENTS.md").write_text("# agent rules\n")
    (tmp_path / ".claude" / "skills").mkdir(parents=True)
    (tmp_path / "openspec" / "changes").mkdir(parents=True)
    (tmp_path / ".omc").mkdir()
    (tmp_path / ".omc" / "project-memory.json").write_text("{}\n")

    client = TestClient(create_app())
    response = client.post("/api/vibe-coding", data={"path": str(tmp_path)})

    assert response.status_code == 200
    assert 'data-codexray-vibe="report"' in response.text
    assert "Vibe Coding" in response.text
    assert "잘한 점" in response.text
    assert "주의할 점" in response.text
    assert "다음 행동" in response.text
    assert "에이전트 지침" in response.text
    assert "AGENTS.md" in response.text


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
    assert "polling every 2 seconds" in response.text
    assert "Cancel Review" in response.text
    assert 'hx-get="/api/review/status/job123"' in response.text


def test_review_cancel_route(monkeypatch) -> None:
    job = ReviewJob(id="job123", root=Path("."), status="cancelled")

    monkeypatch.setattr(routes, "cancel_review_job", lambda job_id: job)
    client = TestClient(create_app())
    response = client.post("/api/review/cancel/job123")
    assert response.status_code == 200
    assert "AI review cancelled" in response.text


def test_review_status_unknown_job_returns_error() -> None:
    client = TestClient(create_app())
    response = client.get("/api/review/status/unknown")
    assert response.status_code == 400
    assert "review job not found" in response.text


def test_browse_folder_updates_path_input(monkeypatch) -> None:
    monkeypatch.setattr(
        routes,
        "choose_folder",
        lambda: FolderPickerResult("/tmp/example"),
    )
    client = TestClient(create_app())
    response = client.post("/api/browse-folder")
    assert response.status_code == 200
    assert 'hx-swap-oob="true"' in response.text
    assert 'value="/tmp/example"' in response.text


def test_browse_folder_cancel_keeps_input(monkeypatch) -> None:
    monkeypatch.setattr(
        routes,
        "choose_folder",
        lambda: FolderPickerResult(None, cancelled=True),
    )
    client = TestClient(create_app())
    response = client.post("/api/browse-folder")
    assert response.status_code == 200
    assert "Folder selection cancelled" in response.text
    assert "path-input" not in response.text


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

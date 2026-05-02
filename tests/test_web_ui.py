from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from typer.testing import CliRunner

import codexray.cli as cli
from codexray.web import create_app
from codexray.web.folder_picker import FolderPickerResult
from codexray.web.jobs import ReviewJob

_FRONTEND_DIST = Path(__file__).resolve().parent.parent / "frontend" / "dist" / "index.html"


def _make_tree(root: Path) -> None:
    (root / "a.py").write_text("from .b import value\n")
    (root / "b.py").write_text("value = 1\n")
    (root / "README.md").write_text("# example\n")


@pytest.mark.skipif(
    not _FRONTEND_DIST.exists(),
    reason="frontend/dist 가 없으면 SPA 라우트도 비활성. cross-platform CI 에서 npm build 생략",
)
def test_main_page_serves_react_spa_when_dist_exists() -> None:
    client = TestClient(create_app())
    response = client.get("/")
    assert response.status_code == 200
    assert '<div id="root"></div>' in response.text
    assert "<title>CodeXray</title>" in response.text


def test_default_path_endpoint_returns_json() -> None:
    client = TestClient(create_app())
    response = client.get("/api/default-path")
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload.get("path"), str) and payload["path"]


def test_briefing_endpoint_starts_job_and_returns_job_id(tmp_path: Path) -> None:
    _make_tree(tmp_path)
    client = TestClient(create_app())
    response = client.post("/api/briefing", json={"path": str(tmp_path)})
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload.get("job_id"), str) and payload["job_id"]


def test_briefing_endpoint_rejects_missing_path() -> None:
    client = TestClient(create_app())
    response = client.post("/api/briefing", json={"path": "/nonexistent/path/zzz"})
    assert response.status_code == 400
    assert "error" in response.json()


def test_path_validation_rejects_missing_path(tmp_path: Path) -> None:
    client = TestClient(create_app())
    response = client.post("/api/inventory", json={"path": str(tmp_path / "missing")})
    assert response.status_code == 400
    assert "찾을 수 없습니다" in response.text


def test_path_validation_rejects_file_path(tmp_path: Path) -> None:
    file_path = tmp_path / "file.py"
    file_path.write_text("x = 1\n")
    client = TestClient(create_app())
    response = client.post("/api/inventory", json={"path": str(file_path)})
    assert response.status_code == 400
    assert "디렉토리가 아닙니다" in response.text


def test_json_analysis_endpoints_return_data(tmp_path: Path) -> None:
    _make_tree(tmp_path)
    client = TestClient(create_app())
    json_endpoints = [
        "/api/inventory",
        "/api/graph",
        "/api/metrics",
        "/api/entrypoints",
        "/api/quality",
        "/api/hotspots",
        "/api/architecture",
    ]
    for endpoint in json_endpoints:
        response = client.post(endpoint, json={"path": str(tmp_path)})
        assert response.status_code == 200, endpoint
        body = response.json()
        assert isinstance(body, dict), endpoint


def test_dashboard_endpoint_returns_html_payload(tmp_path: Path) -> None:
    _make_tree(tmp_path)
    client = TestClient(create_app())
    response = client.post("/api/dashboard", json={"path": str(tmp_path)})
    assert response.status_code == 200
    payload = response.json()
    assert "codexray-dashboard-v1" in payload["html"]
    assert "<!DOCTYPE html>" in payload["html"]


def test_vibe_coding_endpoint_returns_json_report(tmp_path: Path) -> None:
    _make_tree(tmp_path)
    (tmp_path / "AGENTS.md").write_text("# agent rules\n")
    (tmp_path / ".claude" / "skills").mkdir(parents=True)
    (tmp_path / "openspec" / "changes").mkdir(parents=True)
    (tmp_path / ".omc").mkdir()
    (tmp_path / ".omc" / "project-memory.json").write_text("{}\n")

    client = TestClient(create_app())
    response = client.post("/api/vibe-coding", json={"path": str(tmp_path)})

    assert response.status_code == 200
    payload = response.json()
    assert payload["confidence"] in {"low", "medium", "high"}
    assert isinstance(payload.get("evidence"), list) and payload["evidence"]
    paths = {e["path"] for e in payload["evidence"]}
    assert any(p.endswith("AGENTS.md") for p in paths)


def test_review_endpoint_starts_job_and_returns_job_id(tmp_path: Path, monkeypatch) -> None:
    _make_tree(tmp_path)
    calls: list[Path] = []

    def fake_start(root: Path) -> ReviewJob:
        calls.append(root)
        return ReviewJob(id="job123", root=root, status="running")

    import codexray.web.api_v2 as api_v2

    monkeypatch.setattr(api_v2, "start_review_job", fake_start)
    client = TestClient(create_app())
    response = client.post("/api/review", json={"path": str(tmp_path)})
    assert response.status_code == 200
    assert response.json() == {"job_id": "job123"}
    assert calls == [tmp_path.resolve()]


def test_review_cancel_route_returns_cancelled_status(monkeypatch) -> None:
    job = ReviewJob(id="job123", root=Path("."), status="cancelled")
    import codexray.web.api_v2 as api_v2

    monkeypatch.setattr(api_v2, "cancel_review_job", lambda job_id: job)
    client = TestClient(create_app())
    response = client.post("/api/review/cancel/job123")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "cancelled"
    assert payload["job_id"] == "job123"


def test_review_status_unknown_job_returns_404() -> None:
    client = TestClient(create_app())
    response = client.get("/api/review/status/unknown")
    assert response.status_code == 404
    assert "review job not found" in response.text


def test_browse_folder_returns_chosen_path_json(monkeypatch) -> None:
    import codexray.web.folder_picker as folder_picker

    monkeypatch.setattr(
        folder_picker,
        "choose_folder",
        lambda: FolderPickerResult("/tmp/example"),
    )
    client = TestClient(create_app())
    response = client.post("/api/browse-folder")
    assert response.status_code == 200
    payload = response.json()
    assert payload == {"path": "/tmp/example"}


def test_browse_folder_cancelled_returns_json_flag(monkeypatch) -> None:
    import codexray.web.folder_picker as folder_picker

    monkeypatch.setattr(
        folder_picker,
        "choose_folder",
        lambda: FolderPickerResult(None, cancelled=True),
    )
    client = TestClient(create_app())
    response = client.post("/api/browse-folder")
    assert response.status_code == 200
    assert response.json() == {"cancelled": True}


def test_report_endpoint_returns_json(tmp_path: Path) -> None:
    _make_tree(tmp_path)
    client = TestClient(create_app())
    response = client.post("/api/report", json={"path": str(tmp_path)})
    assert response.status_code == 200
    payload = response.json()
    assert "summary" in payload
    assert "markdown" in payload
    assert isinstance(payload["recommendations"], list)


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

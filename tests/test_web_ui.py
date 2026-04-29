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
    ]
    for endpoint in json_endpoints:
        response = client.post(endpoint, json={"path": str(tmp_path)})
        assert response.status_code == 200, endpoint
        body = response.json()
        assert isinstance(body, dict), endpoint


def test_deterministic_endpoints_return_fragments(tmp_path: Path) -> None:
    _make_tree(tmp_path)
    client = TestClient(create_app())
    htmx_only_endpoints = [
        "/api/overview",
    ]
    for endpoint in htmx_only_endpoints:
        response = client.post(endpoint, data={"path": str(tmp_path)})
        assert response.status_code == 200, endpoint
        assert 'data-codexray-result="' in response.text
        assert "Raw JSON" not in response.text
        assert "json-output" not in response.text


def test_analysis_panels_include_split_sidebar(tmp_path: Path) -> None:
    _make_tree(tmp_path)
    client = TestClient(create_app())
    htmx_only_endpoints = [
        "/api/overview",
    ]
    for endpoint in htmx_only_endpoints:
        response = client.post(endpoint, data={"path": str(tmp_path)})
        assert response.status_code == 200, endpoint
        assert "analysis-explainer" in response.text, endpoint
        assert 'id="insights-panel"' in response.text, endpoint
        assert "시니어 인사이트" in response.text, endpoint
        assert "주니어 학습 컨텍스트" in response.text, endpoint
        assert "Generate insights" in response.text, endpoint


def test_dashboard_endpoint_returns_html_payload(tmp_path: Path) -> None:
    _make_tree(tmp_path)
    client = TestClient(create_app())
    response = client.post("/api/dashboard", json={"path": str(tmp_path)})
    assert response.status_code == 200
    payload = response.json()
    assert "codexray-dashboard-v1" in payload["html"]
    assert "<!DOCTYPE html>" in payload["html"]


def test_briefing_endpoint_returns_job_id_json(tmp_path: Path) -> None:
    _make_tree(tmp_path)
    (tmp_path / "AGENTS.md").write_text("# agent rules\n")
    (tmp_path / "docs" / "validation").mkdir(parents=True)
    (tmp_path / "openspec" / "changes").mkdir(parents=True)

    client = TestClient(create_app())
    response = client.post("/api/briefing", json={"path": str(tmp_path)})

    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload.get("job_id"), str) and payload["job_id"]


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


def test_insights_unavailable_when_no_adapter(tmp_path: Path, monkeypatch) -> None:
    _make_tree(tmp_path)
    from codexray.ai.adapters import AIAdapterError

    def fake_select(env):
        raise AIAdapterError("no AI backend available")

    monkeypatch.setattr(routes, "select_adapter", fake_select)
    client = TestClient(create_app())
    response = client.post("/api/insights/inventory", data={"path": str(tmp_path)})
    assert response.status_code == 200
    assert "AI 어댑터 미설정" in response.text
    assert 'id="insights-panel"' in response.text


def test_insights_disabled_for_dashboard_tab(tmp_path: Path) -> None:
    _make_tree(tmp_path)
    client = TestClient(create_app())
    response = client.post("/api/insights/dashboard", data={"path": str(tmp_path)})
    assert response.status_code == 200
    assert "비활성화" in response.text
    assert 'id="insights-panel"' in response.text


def test_insights_unsupported_tab_returns_error(tmp_path: Path) -> None:
    _make_tree(tmp_path)
    client = TestClient(create_app())
    response = client.post("/api/insights/bogus", data={"path": str(tmp_path)})
    assert response.status_code == 400


def test_insights_starts_background_job_on_cache_miss(
    tmp_path: Path, monkeypatch
) -> None:
    _make_tree(tmp_path)
    from codexray.web.jobs import InsightsJob

    class FakeAdapter:
        name = "codex"

    captured: list[tuple[Path, str, str]] = []

    def fake_start(root, tab, raw_json, adapter, key):
        captured.append((root, tab, raw_json[:30]))
        return InsightsJob(
            id="job123", root=root, tab=tab, status="running", cache_key=key
        )

    monkeypatch.setenv("CODEXRAY_CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.setattr(routes, "select_adapter", lambda env: FakeAdapter())
    monkeypatch.setattr(routes, "start_insights_job", fake_start)
    client = TestClient(create_app())
    response = client.post(
        "/api/insights/inventory", data={"path": str(tmp_path)}
    )
    assert response.status_code == 200
    assert "인사이트 생성 중" in response.text
    assert 'hx-get="/api/insights/status/job123"' in response.text
    assert len(captured) == 1
    assert captured[0][1] == "inventory"


def test_insights_cache_hit_returns_ready_without_starting_job(
    tmp_path: Path, monkeypatch
) -> None:
    _make_tree(tmp_path)
    from codexray.web.insights import (
        PROMPT_VERSION,
        InsightBullet,
        InsightResult,
        cache_key,
        cache_put,
    )

    class FakeAdapter:
        name = "codex"

    monkeypatch.setenv("CODEXRAY_CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.setattr(routes, "select_adapter", lambda env: FakeAdapter())

    started: list[str] = []
    monkeypatch.setattr(
        routes,
        "start_insights_job",
        lambda root, tab, raw_json, adapter, key: started.append(tab),
    )

    raw_json = routes._build_raw_json(tmp_path.resolve(), "inventory")
    key = cache_key(
        path=str(tmp_path.resolve()),
        tab="inventory",
        raw_json=raw_json,
        adapter_id="codex",
    )
    cache_put(
        key,
        InsightResult(
            schema_version=1,
            backend="codex",
            prompt_version=PROMPT_VERSION,
            tab="inventory",
            bullets=(
                InsightBullet(tag="risk", observation="X 결합도 높음", implication="회귀 위험"),
                InsightBullet(tag="next", observation="테스트 추가", implication="안전성 확보"),
            ),
        ),
    )

    client = TestClient(create_app())
    response = client.post(
        "/api/insights/inventory", data={"path": str(tmp_path)}
    )
    assert response.status_code == 200
    assert "다시 생성" in response.text
    assert started == []


def test_insights_regenerate_forces_new_job(tmp_path: Path, monkeypatch) -> None:
    _make_tree(tmp_path)
    from codexray.web.insights import (
        PROMPT_VERSION,
        InsightBullet,
        InsightResult,
        cache_key,
        cache_put,
    )
    from codexray.web.jobs import InsightsJob

    class FakeAdapter:
        name = "codex"

    monkeypatch.setenv("CODEXRAY_CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.setattr(routes, "select_adapter", lambda env: FakeAdapter())

    started: list[str] = []

    def fake_start(root, tab, raw_json, adapter, key):
        started.append(tab)
        return InsightsJob(
            id="reg1", root=root, tab=tab, status="running", cache_key=key
        )

    monkeypatch.setattr(routes, "start_insights_job", fake_start)

    raw_json = routes._build_raw_json(tmp_path.resolve(), "inventory")
    key = cache_key(
        path=str(tmp_path.resolve()),
        tab="inventory",
        raw_json=raw_json,
        adapter_id="codex",
    )
    cache_put(
        key,
        InsightResult(
            schema_version=1,
            backend="codex",
            prompt_version=PROMPT_VERSION,
            tab="inventory",
            bullets=(
                InsightBullet(tag="risk", observation="X 결합도 높음", implication="회귀 위험"),
                InsightBullet(tag="next", observation="테스트 추가", implication="안전성 확보"),
            ),
        ),
    )

    client = TestClient(create_app())
    response = client.post(
        "/api/insights/inventory/regenerate", data={"path": str(tmp_path)}
    )
    assert response.status_code == 200
    assert "인사이트 생성 중" in response.text
    assert started == ["inventory"]


def test_insights_cancel_route(monkeypatch) -> None:
    from codexray.web.jobs import InsightsJob

    monkeypatch.setattr(
        routes,
        "cancel_insights_job",
        lambda job_id: InsightsJob(
            id="job123",
            root=Path("."),
            tab="quality",
            status="cancelled",
            cache_key="k",
        ),
    )
    client = TestClient(create_app())
    response = client.post("/api/insights/cancel/job123")
    assert response.status_code == 200
    assert "취소" in response.text
    assert 'id="insights-panel"' in response.text


def test_insights_status_running(monkeypatch) -> None:
    from codexray.web.jobs import InsightsJob

    monkeypatch.setattr(
        routes,
        "get_insights_job",
        lambda job_id: InsightsJob(
            id="r1",
            root=Path("."),
            tab="hotspots",
            status="running",
            cache_key="k",
        ),
    )
    client = TestClient(create_app())
    response = client.get("/api/insights/status/r1")
    assert response.status_code == 200
    assert "인사이트 생성 중" in response.text
    assert 'hx-get="/api/insights/status/r1"' in response.text


def test_insights_status_done(monkeypatch) -> None:
    from codexray.web.insights import (
        PROMPT_VERSION,
        InsightBullet,
        InsightResult,
    )
    from codexray.web.jobs import InsightsJob

    result = InsightResult(
        schema_version=1,
        backend="codex",
        prompt_version=PROMPT_VERSION,
        tab="metrics",
        bullets=(
            InsightBullet(
                tag="risk",
                observation="결합도가 매우 높습니다",
                implication="회귀 위험",
            ),
            InsightBullet(
                tag="next",
                observation="테스트 우선 추가",
                implication="안전성 확보",
            ),
        ),
    )
    monkeypatch.setattr(
        routes,
        "get_insights_job",
        lambda job_id: InsightsJob(
            id="d1",
            root=Path("."),
            tab="metrics",
            status="done",
            cache_key="k",
            result=result,
        ),
    )
    client = TestClient(create_app())
    response = client.get("/api/insights/status/d1")
    assert response.status_code == 200
    assert "결합도가 매우 높습니다" in response.text
    assert "다시 생성" in response.text


def test_insights_status_failed(monkeypatch) -> None:
    from codexray.web.jobs import InsightsJob

    monkeypatch.setattr(
        routes,
        "get_insights_job",
        lambda job_id: InsightsJob(
            id="f1",
            root=Path("."),
            tab="quality",
            status="failed",
            cache_key="k",
            error="codex CLI exit 1",
        ),
    )
    client = TestClient(create_app())
    response = client.get("/api/insights/status/f1")
    assert response.status_code == 500
    assert "AI 호출 실패" in response.text


def test_insights_status_skipped(monkeypatch) -> None:
    from codexray.web.jobs import InsightsJob

    monkeypatch.setattr(
        routes,
        "get_insights_job",
        lambda job_id: InsightsJob(
            id="s1",
            root=Path("."),
            tab="quality",
            status="skipped",
            cache_key="k",
            skip_reason="missing [risk] bullet",
        ),
    )
    client = TestClient(create_app())
    response = client.get("/api/insights/status/s1")
    assert response.status_code == 200
    assert "AI 응답이 형식에 맞지 않음" in response.text


def test_overview_renders_summary_cards(tmp_path: Path) -> None:
    _make_tree(tmp_path)
    client = TestClient(create_app())
    response = client.post("/api/overview", data={"path": str(tmp_path)})
    assert response.status_code == 200
    assert 'data-codexray-summary="cards"' in response.text
    assert "강점" in response.text
    assert "약점" in response.text
    assert "다음 행동" in response.text


def test_report_renders_summary_cards(tmp_path: Path) -> None:
    _make_tree(tmp_path)
    client = TestClient(create_app())
    response = client.post("/api/report", json={"path": str(tmp_path)})
    assert response.status_code == 200
    payload = response.json()
    assert "summary" in payload
    assert "markdown" in payload
    assert isinstance(payload["recommendations"], list)


def test_overview_does_not_call_ai(tmp_path: Path, monkeypatch) -> None:
    _make_tree(tmp_path)
    from codexray.ai.adapters import AIAdapterError

    def boom(env):
        raise AIAdapterError("forced unavailable for AI-not-called test")

    monkeypatch.setattr(routes, "select_adapter", boom)
    client = TestClient(create_app())
    response = client.post("/api/overview", data={"path": str(tmp_path)})
    assert response.status_code == 200
    assert 'data-codexray-summary="cards"' in response.text


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

## Why

현재 CodeXray는 8개 CLI 명령으로 MVP 기능을 모두 제공하지만, 사용자가 매번 명령어와 리다이렉션을 기억해야 한다. 사용자의 다음 의도는 "명령어를 치는 도구"에서 "UX/UI로 제어하는 1인 로컬 도구"로 전환하는 것이다.

이번 변경은 분석 알고리즘을 새로 만들지 않는다. 기존 `inventory`, `graph`, `metrics`, `entrypoints`, `quality`, `hotspots`, `report`, `dashboard`, `review`를 localhost 웹 UI에서 실행하고 결과를 한 화면에서 확인하게 한다. `constraints.md`의 "로컬 실행 우선, SaaS 호스팅 X" 원칙을 유지한다.

## What Changes

- 새 CLI 진입점: `codexray serve [--host 127.0.0.1] [--port 8080] [--no-browser]`
- FastAPI 기반 localhost 단일 사용자 서버 추가
- htmx + Jinja2 기반 서버 주도 UI 추가
  - 빌드 파이프라인 없음
  - 경로 입력 + 최근 5개 경로 localStorage history
  - 9개 탭: Overview, Inventory, Graph, Metrics, Hotspots, Quality, Entrypoints, Report, Dashboard, Review
  - 결과 패널 inline 렌더링: JSON pretty, Markdown HTML, Dashboard iframe
- API/fragment endpoint 추가
  - `GET /` — 메인 페이지
  - `POST /api/overview`
  - `POST /api/inventory`
  - `POST /api/graph`
  - `POST /api/metrics`
  - `POST /api/entrypoints`
  - `POST /api/quality`
  - `POST /api/hotspots`
  - `POST /api/report`
  - `POST /api/dashboard`
  - `POST /api/review`
- AI review는 별도 탭에서 명시 클릭해야 실행되고, UI에 1~5분 소요 가능성을 표시한다.
- 잘못된 path는 HTTP 400 결과 fragment로 표시하고 서버 프로세스는 유지한다.

## Capabilities

### New Capabilities

- `web-ui`: CodeXray 분석 명령을 localhost 웹 UI에서 실행하고 결과를 탭별 panel로 표시하는 능력. 1차 구현은 로컬 단일 사용자, htmx fragment swap, Jinja2 template, FastAPI server lifecycle에 집중한다.

### Modified Capabilities

- `cli`: `serve` 서브커맨드만 추가한다. 기존 분석 명령의 stdout/stderr 계약은 변경하지 않는다.

## Impact

- 신규 의존성: `fastapi`, `uvicorn`, `jinja2`
- 신규 코드: `src/codexray/web/`
  - `server.py` — FastAPI app factory, uvicorn 실행, 브라우저 오픈
  - `routes.py` — page + analysis endpoint
  - `schemas.py` 또는 `types.py` — request/result DTO
  - `render.py` — JSON/Markdown/HTML fragment 렌더 보조
  - `templates/` — Jinja2 page/fragments
  - `static/` — CSS/JS (htmx는 CDN 또는 vendored static 중 design에서 결정)
- CLI 변경: `src/codexray/cli.py`
- 테스트 추가: route smoke, path validation, fragment markers, CLI option wiring
- 검증: CodeXray 자기 자신 + CivilSim에서 HTTP endpoint smoke와 결과 capture를 `docs/validation/web-ui-{self,civilsim}.md`로 보관

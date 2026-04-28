# web-ui Specification

## Purpose
TBD - created by archiving change add-web-ui. Update Purpose after archive.
## Requirements
### Requirement: Web UI CLI 진입점
The system SHALL expose a `codexray serve` command that starts a localhost web UI server for controlling CodeXray analysis commands.

#### Scenario: 기본 서버 실행
- **WHEN** 사용자가 `codexray serve`를 실행하면
- **THEN** 시스템은 `127.0.0.1:8080`에서 HTTP 서버를 시작한다

#### Scenario: 포트 지정
- **WHEN** 사용자가 `codexray serve --port 8090`을 실행하면
- **THEN** 시스템은 `127.0.0.1:8090`에서 HTTP 서버를 시작한다

#### Scenario: 브라우저 자동 열림 비활성화
- **WHEN** 사용자가 `codexray serve --no-browser`를 실행하면
- **THEN** 시스템은 서버를 시작하지만 브라우저를 자동으로 열지 않는다

### Requirement: 메인 페이지
The system SHALL serve a main page at `GET /` with a path input, recent path selector, analysis tabs, and a result panel.

#### Scenario: 메인 페이지 로드
- **WHEN** 브라우저가 `GET /`를 요청하면
- **THEN** 시스템은 HTTP 200 HTML 응답을 반환하고 본문에 path input, result panel, and analysis tabs를 포함한다

#### Scenario: 최근 path 저장
- **WHEN** 사용자가 UI에서 분석 path를 제출하면
- **THEN** 브라우저는 localStorage에 최근 path를 최대 5개까지 저장할 수 있다

### Requirement: htmx Jinja UI
The system SHALL implement the first web UI with server-rendered Jinja2 templates and htmx fragment swaps without a JavaScript build pipeline.

#### Scenario: htmx fragment swap
- **WHEN** 사용자가 Inventory, Graph, Metrics, Hotspots, Quality, Entrypoints, Report, Dashboard, or Review 탭을 클릭하면
- **THEN** 브라우저는 htmx request를 보내고 result panel을 서버가 반환한 HTML fragment로 교체한다

### Requirement: Path validation
The system SHALL validate submitted paths before running analysis.

#### Scenario: 유효한 디렉토리 path
- **WHEN** 사용자가 존재하는 디렉토리 path를 제출하면
- **THEN** 시스템은 해당 디렉토리에 대해 요청된 분석을 실행하고 HTTP 200 fragment를 반환한다

#### Scenario: 존재하지 않는 path
- **WHEN** 사용자가 존재하지 않는 path를 제출하면
- **THEN** 시스템은 HTTP 400 오류 fragment를 반환하고 서버 프로세스는 계속 실행된다

#### Scenario: 파일 path
- **WHEN** 사용자가 디렉토리가 아닌 파일 path를 제출하면
- **THEN** 시스템은 HTTP 400 오류 fragment를 반환하고 분석 builder를 호출하지 않는다

### Requirement: Analysis endpoints
The system SHALL provide web endpoints for overview, inventory, graph, metrics, entrypoints, quality, hotspots, report, dashboard, and review.

#### Scenario: 결정론적 분석 endpoint
- **WHEN** 유효한 path로 `/api/inventory`, `/api/graph`, `/api/metrics`, `/api/entrypoints`, `/api/quality`, `/api/hotspots`, `/api/report`, or `/api/dashboard`에 POST 요청을 보내면
- **THEN** 시스템은 기존 CodeXray builder를 사용해 결과 fragment를 반환한다

#### Scenario: Overview endpoint
- **WHEN** 유효한 path로 `/api/overview`에 POST 요청을 보내면
- **THEN** 시스템은 전체 grade, 주요 hotspot, 파일/언어 요약을 포함한 summary fragment를 반환한다

### Requirement: Result rendering
The system SHALL render analysis results inline in the result panel.

#### Scenario: JSON 계열 결과
- **WHEN** inventory, graph, metrics, entrypoints, quality, hotspots, or review 결과를 표시하면
- **THEN** 시스템은 schema_version을 포함하는 pretty JSON을 HTML escaped fragment로 렌더링한다

#### Scenario: Report 결과
- **WHEN** report 결과를 표시하면
- **THEN** 시스템은 Markdown report를 HTML escaped readable fragment로 렌더링한다

#### Scenario: Dashboard 결과
- **WHEN** dashboard 결과를 표시하면
- **THEN** 시스템은 기존 dashboard HTML을 iframe 또는 동등한 격리 컨테이너 안에 렌더링한다

### Requirement: AI review opt-in
The system SHALL make AI review an explicit user action separate from deterministic analysis.

#### Scenario: Review 탭 경고
- **WHEN** 사용자가 Review 탭을 볼 때
- **THEN** UI는 AI review가 1~5분 걸릴 수 있고 명시 실행이 필요하다는 경고를 표시한다

#### Scenario: 명시 실행
- **WHEN** 사용자가 Review 실행을 명시적으로 요청하면
- **THEN** 시스템은 background job을 시작하고 진행 상태 fragment를 즉시 반환한다

#### Scenario: Review 상태 polling
- **WHEN** background AI review job이 완료되면
- **THEN** 시스템은 status endpoint를 통해 schema_version을 포함하는 pretty JSON 결과 fragment를 반환한다

### Requirement: Performance budget
The system SHALL return meaningful HTTP results within 5 seconds for deterministic endpoints on the validation codebases.

#### Scenario: Self validation
- **WHEN** CodeXray repository path로 deterministic endpoint smoke를 실행하면
- **THEN** 각 endpoint는 5초 내 HTTP 200과 의미 있는 result marker를 반환한다

#### Scenario: CivilSim validation
- **WHEN** CivilSim repository path로 deterministic endpoint smoke를 실행하면
- **THEN** 각 endpoint는 5초 내 HTTP 200과 의미 있는 result marker를 반환한다

### Requirement: Validation capture
The system SHALL capture web UI validation results for both validation codebases.

#### Scenario: Validation documents
- **WHEN** add-web-ui 구현 검증을 완료하면
- **THEN** `docs/validation/web-ui-self.md` and `docs/validation/web-ui-civilsim.md` contain endpoint smoke results and representative output summaries

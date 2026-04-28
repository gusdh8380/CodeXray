# web-ui Specification

## Purpose
The web-ui capability provides the `codexray serve` CLI: it runs a localhost FastAPI server (default `127.0.0.1:8080`) that exposes every CodeXray analysis builder and the AI review through a single htmx + Jinja2 page. Results render inline as decision-oriented HTML with a Korean senior-developer commentary sidebar, and AI review is an explicit opt-in background job with cancel and status polling. The capability ships without a JavaScript build pipeline to stay aligned with the project's local-first constraint.

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
The system SHALL serve a main page at `GET /` with a path input, recent path selector, analysis tabs, status text, and a result panel.

#### Scenario: 메인 페이지 로드
- **WHEN** 브라우저가 `GET /`를 요청하면
- **THEN** 시스템은 HTTP 200 HTML 응답을 반환하고 본문에 path input, status text, result panel, and analysis tabs를 포함한다

#### Scenario: 최근 path 저장
- **WHEN** 사용자가 UI에서 분석 path를 제출하면
- **THEN** 브라우저는 localStorage에 최근 path를 최대 5개까지 저장할 수 있다

#### Scenario: Overview 자동 로드
- **WHEN** 메인 페이지 JavaScript가 초기화되면
- **THEN** 브라우저는 기본 path로 Overview 탭을 자동 실행한다

### Requirement: htmx Jinja UI
The system SHALL implement the first web UI with server-rendered Jinja2 templates and htmx fragment swaps without a JavaScript build pipeline.

#### Scenario: htmx fragment swap
- **WHEN** 사용자가 Inventory, Graph, Metrics, Hotspots, Quality, Entrypoints, Report, Dashboard, or Review 탭을 클릭하면
- **THEN** 브라우저는 htmx request를 보내고 result panel을 서버가 반환한 HTML fragment로 교체한다

#### Scenario: Active tab 표시
- **WHEN** 사용자가 analysis tab을 클릭하면
- **THEN** UI는 해당 tab을 active 상태로 표시한다

#### Scenario: Loading 표시
- **WHEN** analysis htmx request가 진행 중이면
- **THEN** UI는 result panel에 loading 상태를 표시하고 status text를 갱신한다

#### Scenario: Enter 재실행
- **WHEN** 사용자가 path input에서 Enter를 누르면
- **THEN** UI는 현재 active tab을 같은 path로 다시 실행한다

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
The system SHALL render analysis results inline in the result panel as readable decision-oriented HTML by default, while preserving raw JSON as secondary detail when JSON exists.

#### Scenario: JSON 계열 결과
- **WHEN** inventory, graph, metrics, entrypoints, quality, hotspots, or review 결과를 표시하면
- **THEN** 시스템은 요약, 해석, table 또는 breakdown을 포함하는 readable HTML을 렌더링하고 raw JSON을 collapsible detail로 제공한다

#### Scenario: 한국어 설명 sidebar
- **WHEN** inventory, graph, metrics, hotspots, quality, entrypoints, or report 결과를 표시하면
- **THEN** 시스템은 오른쪽 영역에 한국어로 시니어 개발자 관점의 의미와 다음 행동을 설명한다

#### Scenario: Report 결과
- **WHEN** report 결과를 표시하면
- **THEN** 시스템은 Markdown report를 sectioned readable HTML로 렌더링하고 핵심 grade와 recommendation을 상단에 표시한다

#### Scenario: Dashboard 결과
- **WHEN** dashboard 결과를 표시하면
- **THEN** 시스템은 기존 dashboard HTML을 넓은 workspace iframe에 렌더링하고 고정된 작은 내부창처럼 보이지 않게 한다

### Requirement: AI review opt-in
The system SHALL make AI review an explicit user action separate from deterministic analysis and SHALL show clear running feedback while the background review job is active.

#### Scenario: Review 탭 경고
- **WHEN** 사용자가 Review 탭을 볼 때
- **THEN** UI는 AI review가 1~5분 걸릴 수 있고 명시 실행이 필요하다는 경고를 표시한다

#### Scenario: 명시 실행
- **WHEN** 사용자가 Review 실행을 명시적으로 요청하면
- **THEN** 시스템은 background job을 시작하고 진행 상태 fragment를 즉시 반환한다

#### Scenario: Review running feedback
- **WHEN** background AI review job이 실행 중이면
- **THEN** UI는 polling 중임과 cancel control을 표시하고 다른 탭을 계속 사용할 수 있음을 보여준다

#### Scenario: Review 취소
- **WHEN** 사용자가 running AI review job에서 Cancel을 누르면
- **THEN** 시스템은 job을 cancelled 상태로 표시하고 cancelled fragment를 반환한다

#### Scenario: Review 상태 polling
- **WHEN** background AI review job이 완료되면
- **THEN** 시스템은 status endpoint를 통해 schema_version을 포함하는 readable review result fragment를 반환한다

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

### Requirement: Theme mode
The system SHALL provide light and dark theme modes for the web UI and persist the user's preference in browser localStorage.

#### Scenario: Theme toggle
- **WHEN** 사용자가 theme toggle을 누르면
- **THEN** UI는 light와 dark mode 사이를 전환한다

#### Scenario: Theme persistence
- **WHEN** 사용자가 theme을 선택한 뒤 페이지를 다시 열면
- **THEN** 브라우저는 저장된 theme preference를 적용한다

### Requirement: Folder picker
The system SHALL provide a path Browse control that fills the path input from a local folder picker when the host OS supports it.

#### Scenario: macOS folder 선택
- **WHEN** macOS 사용자가 Browse 버튼을 눌러 폴더를 선택하면
- **THEN** 시스템은 선택된 POSIX path를 path input에 채운다

#### Scenario: folder 선택 취소
- **WHEN** 사용자가 folder picker를 취소하면
- **THEN** 시스템은 기존 path input 값을 유지하고 취소 상태를 표시한다

#### Scenario: 지원하지 않는 OS
- **WHEN** folder picker가 지원되지 않는 OS에서 Browse 버튼을 누르면
- **THEN** 시스템은 수동 path 입력이 필요하다는 오류 상태를 표시한다


## MODIFIED Requirements

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
- **THEN** UI는 polling 중임을 표시하고 다른 탭을 계속 사용할 수 있음을 보여준다

#### Scenario: Review 상태 polling
- **WHEN** background AI review job이 완료되면
- **THEN** 시스템은 status endpoint를 통해 schema_version을 포함하는 pretty JSON 결과 fragment를 반환한다

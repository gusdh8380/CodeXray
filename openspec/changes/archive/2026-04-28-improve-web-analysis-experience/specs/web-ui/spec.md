## MODIFIED Requirements

### Requirement: Result rendering
The system SHALL render analysis results inline in the result panel as readable decision-oriented HTML by default, while preserving raw JSON as secondary detail when JSON exists.

#### Scenario: JSON 계열 결과
- **WHEN** inventory, graph, metrics, entrypoints, quality, hotspots, or review 결과를 표시하면
- **THEN** 시스템은 요약, 해석, table 또는 breakdown을 포함하는 readable HTML을 렌더링하고 raw JSON을 collapsible detail로 제공한다

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

## ADDED Requirements

### Requirement: Theme mode
The system SHALL provide light and dark theme modes for the web UI and persist the user's preference in browser localStorage.

#### Scenario: Theme toggle
- **WHEN** 사용자가 theme toggle을 누르면
- **THEN** UI는 light와 dark mode 사이를 전환한다

#### Scenario: Theme persistence
- **WHEN** 사용자가 theme을 선택한 뒤 페이지를 다시 열면
- **THEN** 브라우저는 저장된 theme preference를 적용한다

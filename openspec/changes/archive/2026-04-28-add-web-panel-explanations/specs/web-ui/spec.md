## MODIFIED Requirements

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

## ADDED Requirements

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

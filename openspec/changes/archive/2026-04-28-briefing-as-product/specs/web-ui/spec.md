## ADDED Requirements

### Requirement: 분석 시작 버튼
The system SHALL provide an explicit "분석하기" button that starts Briefing analysis for the entered path, making the analysis trigger obvious regardless of which tab was previously active.

#### Scenario: 버튼 클릭으로 분석 시작
- **WHEN** 사용자가 경로를 입력하고 "분석하기" 버튼을 클릭하면
- **THEN** 시스템은 Briefing 탭을 active로 설정하고 /api/briefing 요청을 실행하며 result-panel을 로딩 상태로 업데이트한다

#### Scenario: 다른 경로로 재분석
- **WHEN** 사용자가 경로를 변경하고 "분석하기" 버튼을 클릭하면
- **THEN** 시스템은 새 경로로 Briefing 분석을 시작한다

### Requirement: 상세 분석 접기
The system SHALL group all non-Briefing analysis tabs into a collapsible "상세 분석" section below the result panel, keeping them accessible but not prominent.

#### Scenario: 상세 분석 섹션 기본 상태
- **WHEN** 메인 페이지가 로드되거나 분석이 완료되면
- **THEN** Overview, Inventory, Metrics, Quality, Hotspots, Report, Review, Graph, Entrypoints, Dashboard, Vibe Coding 탭은 접힌 상세 분석 섹션 안에 위치한다

#### Scenario: 상세 분석 펼치기
- **WHEN** 사용자가 "상세 분석 보기"를 클릭하면
- **THEN** 섹션이 펼쳐지고 기존 탭 버튼들이 표시되어 클릭할 수 있다

### Requirement: 대시보드 노드 레이아웃 수정
The system SHALL render the dependency graph dashboard with all nodes visible within the viewport at all times.

#### Scenario: 노드 뷰포트 유지
- **WHEN** 대시보드 그래프가 렌더링되면
- **THEN** 모든 노드는 SVG 뷰포트 경계 내에 위치하며 스크롤 없이 볼 수 있다

#### Scenario: 중요 노드 강조
- **WHEN** 대시보드 그래프가 렌더링되면
- **THEN** coupling이 높은 상위 노드는 크기 또는 색상으로 시각적으로 강조된다

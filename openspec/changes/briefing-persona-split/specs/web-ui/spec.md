## ADDED Requirements

### Requirement: 페르소나 영역 분리
The web UI SHALL maintain a hard separation between the Briefing area (top of the page) and the Detailed Analysis toggle (below) so that each area serves a single, primary audience without compromise.

#### Scenario: 브리핑 영역은 비개발자 청자 영역
- **WHEN** Briefing 화면 상단(executive, architecture, quality_risk, vibe coding section, next actions, key insight, intent alignment)이 렌더링되면
- **THEN** 모든 텍스트는 비개발자 바이브코더가 1차 청자라는 가정하에 표시되며, 메트릭 용어를 직접 노출하지 않는다 (codebase-briefing 의 "Plain-language technical translation" 요구사항을 따른다)

#### Scenario: 상세 분석 토글은 개발자 청자 영역
- **WHEN** Briefing 화면에서 사용자가 상세 분석 토글(미시 분석 탭들 — Hotspots, Inventory, Code Metrics, Code Quality, Dependency Graph, Entrypoints, Vibe Coding Tab, Report)을 펼치면
- **THEN** 그 영역의 시각화·표·메트릭 표현은 개발자 청자 가정(메트릭 용어 직접 노출 OK)하에 그대로 유지되며 비개발자 친화 톤으로 다시 쓰지 않는다

#### Scenario: 영역 간 일관성
- **WHEN** Briefing 영역이 어떤 사실(예: hotspot 개수, coupling 상위 파일)을 평어로 인용하고
- **AND** 사용자가 같은 사실을 상세 분석 토글에서 메트릭 형태로 볼 수 있어야 하면
- **THEN** 두 영역의 데이터 소스는 동일하고 (briefing 평어가 메트릭의 부정확한 요약이 아니라 같은 결정론적 데이터의 다른 표현이어야 한다), 토글 영역에는 같은 메트릭의 raw 형태가 유지된다

#### Scenario: 영역 분리 위반 방지
- **WHEN** 새로운 화면 요소를 Briefing 영역에 추가할 때
- **THEN** 해당 요소의 텍스트가 메트릭 용어를 도입하지 않는지 codebase-briefing 의 "Plain-language technical translation" 요구사항으로 검증한다 (위반 시 토글 영역으로 이동 또는 평어 번역)

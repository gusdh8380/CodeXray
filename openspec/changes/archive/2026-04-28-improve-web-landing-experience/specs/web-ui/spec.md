## ADDED Requirements

### Requirement: Raw JSON 제거
The system SHALL NOT render raw JSON blocks in any analysis tab result panel.

#### Scenario: 분석 탭 결과 렌더링
- **WHEN** 분석 탭이 결과를 렌더링하면
- **THEN** 결과 패널에 raw JSON 블록이 포함되지 않는다

### Requirement: Insight 텍스트 한국어
The system SHALL display all analysis insight texts in Korean.

#### Scenario: Hotspots insight 텍스트
- **WHEN** Hotspots 탭이 렌더링되면
- **THEN** insight 텍스트가 한국어로 표시된다

#### Scenario: AI Review insight 텍스트
- **WHEN** AI Review 탭이 렌더링되면
- **THEN** insight 텍스트가 한국어로 표시된다

### Requirement: 상세 탭 시각 구분
The system SHALL visually separate summary tabs from detail tabs using a divider.

#### Scenario: 탭 구분선 표시
- **WHEN** 메인 페이지가 로드되면
- **THEN** 주요 탭(Briefing~Review) 과 상세 탭(Graph/Entrypoints/Dashboard/Vibe Coding) 사이에 시각적 구분선이 표시된다

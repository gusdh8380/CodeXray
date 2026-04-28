## ADDED Requirements

### Requirement: Overview strengths/weaknesses/actions cards
The system SHALL render three card sections — Strengths, Weaknesses, Next Actions — in the Overview tab main area above the existing summary metrics, each listing up to 3 deterministic items with evidence citations. The cards SHALL be rendered without AI calls and within the existing 5-second performance budget.

#### Scenario: 카드 위치
- **WHEN** 사용자가 Overview 탭을 보면
- **THEN** 메인 영역 상단에 Strengths · Weaknesses · Next Actions 세 카드가 노출되고 그 아래에 기존 summary 메트릭이 표시된다

#### Scenario: 항목 fallback
- **WHEN** 어느 카드의 summary 항목이 0개이면
- **THEN** 해당 카드는 항목 list 대신 "특이사항 없음" 안내 텍스트를 표시한다

#### Scenario: 근거 인용
- **WHEN** Strengths · Weaknesses · Next Actions 항목이 표시되면
- **THEN** 각 항목 본문은 file path 또는 dimension 이름과 score / grade / count 같은 수치 근거를 포함한다

#### Scenario: AI 미사용
- **WHEN** Overview 탭이 렌더링되면
- **THEN** 시스템은 AI 어댑터를 호출하지 않고 result fragment를 반환한다

### Requirement: Report tab strengths/weaknesses/actions sections
The system SHALL render Strengths, Weaknesses, and Next Actions sections at the top of the Report tab readable HTML, mirroring the Markdown structure with up to 3 items each and mandatory evidence citation.

#### Scenario: 위치
- **WHEN** 사용자가 Report 탭을 보면
- **THEN** readable HTML 상단에 Strengths · Weaknesses · Next Actions 섹션이 등장하고 그 아래에 기존 Recommendations · Markdown 본문이 표시된다

#### Scenario: 항목 일관성
- **WHEN** 같은 path로 `codexray report`(CLI)와 Web Report 탭을 비교하면
- **THEN** Strengths · Weaknesses · Next Actions의 항목 수와 본문 텍스트는 같은 path에 대해 동일하다

#### Scenario: AI 미사용
- **WHEN** Report 탭이 렌더링되면
- **THEN** 시스템은 AI 어댑터를 호출하지 않는다

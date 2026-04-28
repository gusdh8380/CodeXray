## ADDED Requirements

### Requirement: Strengths/Weaknesses/Actions section
The system SHALL render a "## Strengths" section, a "## Weaknesses" section, and a "## Next Actions" section in the Markdown report, each listing up to 3 deterministic rule-based items with mandatory evidence citation. The three sections SHALL appear after "## Overall Grade" and before "## Top Hotspots".

#### Scenario: 위치
- **WHEN** `codexray report <path>` Markdown 출력을 보면
- **THEN** "## Strengths", "## Weaknesses", "## Next Actions" 섹션이 "## Overall Grade" 다음, "## Top Hotspots" 이전 순서로 등장한다

#### Scenario: 항목 cap
- **WHEN** summary 빌더가 4개 이상 강점·약점·다음 행동 항목을 산출하면
- **THEN** Markdown 각 섹션은 정확히 3개 항목만 표시한다

#### Scenario: 항목 fallback
- **WHEN** summary 빌더가 어느 한 섹션에서 0개 항목을 산출하면
- **THEN** 해당 섹션은 항목 list 대신 "(특이사항 없음)" 안내 텍스트를 포함한다

#### Scenario: 근거 인용
- **WHEN** "Strengths", "Weaknesses", "Next Actions" 섹션 항목이 출력되면
- **THEN** 각 항목 본문은 file path 또는 dimension 이름과 score / grade / count 같은 수치 근거를 포함한다

#### Scenario: 결정론
- **WHEN** 같은 트리에 대해 `codexray report`를 두 번 같은 날짜에 실행하면
- **THEN** "Strengths", "Weaknesses", "Next Actions" 섹션의 stdout 바이트가 동일하다

## ADDED Requirements

### Requirement: 다음 행동 3 카테고리 그룹 렌더링
The system SHALL render the "지금 뭘 해야 해" section as three categorized groups — 코드 / 구조 / 바이브코딩 — so the user can scan recommendations by their nature.

#### Scenario: 카테고리 그룹 표시
- **WHEN** 다음 행동 섹션이 렌더링되면
- **THEN** UI는 `code`, `structural`, `vibe_coding` 세 카테고리를 각각 별도 그룹으로 표시하며 각 그룹은 한국어 헤더("코드 측면", "구조 측면", "바이브코딩 측면")를 포함한다

#### Scenario: 빈 카테고리 숨김
- **WHEN** 카테고리에 추천 항목이 0개이면
- **THEN** UI는 해당 카테고리 그룹을 화면에 표시하지 않는다

#### Scenario: 카테고리 순서 고정
- **WHEN** 다음 행동 섹션이 렌더링되면
- **THEN** 그룹 순서는 코드 → 구조 → 바이브코딩 순서로 고정되며 카테고리간 순서는 데이터에 의해 바뀌지 않는다

### Requirement: 다음 행동 검토 경고 배너
The system SHALL display an explicit warning banner above the "지금 뭘 해야 해" section so the user reviews recommendations before applying them.

#### Scenario: 경고 배너 항상 표시
- **WHEN** 다음 행동 섹션이 렌더링되면
- **THEN** 섹션 상단에 amber 톤 경고 배너가 표시되며 배너는 "AI가 자동 생성한 추천이라 그대로 적용 시 부적절할 수 있으니 검토 후 진행하세요" 라는 의미의 한국어 문구를 포함한다

#### Scenario: 경고 배너 dismissable 아님
- **WHEN** 사용자가 배너를 클릭하거나 다시 분석을 실행해도
- **THEN** 배너는 사라지지 않고 항상 표시된다

#### Scenario: 라이트/다크 시각 일관
- **WHEN** 사용자가 라이트/다크 테마를 토글하면
- **THEN** 경고 배너는 두 테마 모두에서 가독성을 유지한다 (amber 톤이지만 너무 자극적이지 않음)

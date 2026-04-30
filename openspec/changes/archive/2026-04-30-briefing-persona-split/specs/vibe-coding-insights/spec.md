## MODIFIED Requirements

### Requirement: 행동+왜+증거 형식의 다음 행동
The system SHALL produce next process action recommendations as quadruples of `action`, `reason`, analysis `evidence`, and `ai_prompt`. The `ai_prompt` field is a non-developer-ready text that can be pasted into the next AI session as-is.

#### Scenario: 행동 항목 구조
- **WHEN** 다음 행동이 생성되면
- **THEN** 각 항목은 `action`, `reason`, `evidence`, `ai_prompt` 네 필드를 모두 포함한다

#### Scenario: evidence는 분석 결과 인용
- **WHEN** 행동 항목의 evidence가 생성되면
- **THEN** evidence 필드는 분석에서 도출된 구체적 수치 또는 파일 경로를 포함한다 (예: "Hotspot 23개", "fix 비율 60%", "GameManager.cs coupling 45")

#### Scenario: reason은 왜 그 행동인지 설명
- **WHEN** 행동 항목의 reason이 생성되면
- **THEN** reason 필드는 evidence와 action의 인과 관계를 한국어 한 문장으로 설명한다

#### Scenario: ai_prompt는 3단 구조를 따른다
- **WHEN** 행동 항목의 `ai_prompt` 가 비어있지 않게 생성되면
- **THEN** ai_prompt 텍스트는 codebase-briefing 의 "Next action AI 프롬프트 3단 구조" 요구사항(필수 3 라벨 + 자족적 컨텍스트 + 검증 체크리스트)을 따른다

#### Scenario: 항목 수 제한
- **WHEN** 다음 행동이 생성되면
- **THEN** 항목 수는 최대 3개로 제한되고 우선순위 순으로 정렬된다

### Requirement: 바이브코딩 미감지 시 시작 가이드
The system SHALL provide a starter guide when vibe coding is not detected, recommending concrete first steps. Each starter item SHALL include an `ai_prompt` that follows the same 3-stage structure as next-action items so the non-developer user can paste it directly into the next AI session.

#### Scenario: 시작 가이드 항목
- **WHEN** 레포가 바이브코딩 미감지로 분류되면
- **THEN** 결과는 "전통 방식. 바이브코딩 시작한다면 첫 걸음은?" 문구와 함께 첫 단계 추천 항목을 포함한다

#### Scenario: 추천 첫 단계
- **WHEN** 시작 가이드가 생성되면
- **THEN** 추천은 최소 `CLAUDE.md` 작성, 의도 문서화, 명세 도입을 포함하며 각 항목은 행동+왜+해당 레포의 현재 상태 인용 형식을 따른다

#### Scenario: 시작 가이드 ai_prompt 도 3단 구조
- **WHEN** 시작 가이드 항목의 `ai_prompt` 가 생성되면
- **THEN** ai_prompt 텍스트는 codebase-briefing 의 "Next action AI 프롬프트 3단 구조" 요구사항을 따른다 (`[현재 프로젝트]`, `[해줄 일]`, `[끝나고 확인]` 라벨 필수)

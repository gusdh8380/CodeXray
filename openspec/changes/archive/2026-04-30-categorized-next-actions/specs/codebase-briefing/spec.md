## ADDED Requirements

### Requirement: 다음 행동 카테고리 분류
The system SHALL categorize each next-action recommendation into one of three buckets — `code`, `structural`, or `vibe_coding` — so the user can quickly identify what kind of action a recommendation is.

#### Scenario: 카테고리 필드 존재
- **WHEN** briefing 결과의 `next_actions` 항목이 직렬화되면
- **THEN** 각 항목은 `category` 필드를 포함하며 값은 `code`, `structural`, `vibe_coding` 중 하나이다

#### Scenario: AI 가 code/structural 카테고리 분류
- **WHEN** AI 해석이 다음 행동을 생성하면
- **THEN** AI 는 `code`(코드 측면 — 함수/모듈 단위의 변경, 테스트 보강, 에러 처리)와 `structural`(구조 측면 — 모듈 분리, 의존성 정리, 아키텍처) 두 카테고리로 직접 분류해서 반환한다

#### Scenario: vibe_coding 카테고리는 vibe_insights 에서 합성
- **WHEN** briefing payload 가 빌드되면
- **THEN** `vibe_coding` 카테고리 항목은 AI 가 직접 생성하지 않고 `vibe_insights.next_actions` 또는 `vibe_insights.starter_guide` 의 항목을 `category="vibe_coding"` 으로 표시해 평면 리스트에 합쳐진다

#### Scenario: 카테고리 누락 시 fallback
- **WHEN** AI 응답에서 항목의 `category` 필드가 누락되거나 허용된 값이 아니면
- **THEN** 시스템은 해당 항목의 카테고리를 `code` 로 강제한다

#### Scenario: 카테고리당 항목 수 제한
- **WHEN** 다음 행동이 직렬화되면
- **THEN** 각 카테고리는 최대 3개 항목을 가지며 카테고리가 비어있어도 (0개) 허용된다

## MODIFIED Requirements

### Requirement: AI 해석 레이어
The system SHALL pass raw source code excerpts and git history to the codex/claude CLI adapter to generate Korean narrative interpretations for each Briefing section.

#### Scenario: 원본 코드 번들 생성
- **WHEN** briefing 분석이 실행되면
- **THEN** 시스템은 README, AGENTS.md, CLAUDE.md, docs/intent.md, 진입점 파일, coupling 상위 파일을 토큰 제한 안에서 묶은 raw code bundle을 만든다

#### Scenario: 보조 메트릭 포함
- **WHEN** raw code bundle이 만들어지면
- **THEN** bundle은 inventory, metrics, quality, hotspots의 핵심 수치를 보조 자료로 함께 포함한다

#### Scenario: AI 해석 호출
- **WHEN** bundle이 준비되면
- **THEN** 시스템은 codex CLI를 우선 사용하고 사용 불가 시 claude CLI로 폴백하여 다섯 섹션 각각에 대한 한국어 서술을 요청한다

#### Scenario: AI 해석 결과 구조
- **WHEN** AI 호출이 성공하면
- **THEN** 결과는 다섯 섹션 별 서술 텍스트를 포함하고 `next_actions` 항목은 `{action, reason, evidence, ai_prompt, category}` 다섯 필드를 가지며 `category` 는 `code` 또는 `structural` 이다 (`vibe_coding` 은 백엔드가 합성)

#### Scenario: AI 미사용 시 결정론적 폴백
- **WHEN** AI 어댑터가 사용 불가능하거나 호출이 실패하면
- **THEN** 시스템은 결정론적 템플릿 서술을 사용하고 폴백 플래그를 포함한다

### Requirement: Deterministic briefing serialization
The system SHALL serialize briefing data with `schema_version: 3`, deterministic ordering, and root-relative POSIX paths where paths are present.

#### Scenario: schema_version 변경
- **WHEN** briefing 결과가 직렬화되면
- **THEN** 결과의 schema_version 필드는 `3` 이고 5개 섹션 + 카테고리 분류된 next_actions 구조를 반영한다

#### Scenario: 결정론적 부분 반복 가능
- **WHEN** 동일 레포 상태로 두 번 분석하면
- **THEN** 결정론적 부분(섹션 데이터, 메트릭, 타임라인, vibe_coding 카테고리 항목)의 직렬화 결과는 byte-identical이며 AI 서술은 별도 캐시 키로 관리된다

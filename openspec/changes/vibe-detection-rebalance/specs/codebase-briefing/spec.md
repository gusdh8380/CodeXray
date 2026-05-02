## MODIFIED Requirements

### Requirement: Briefing composition
The system SHALL build a codebase briefing model composed of four to five top-level sections that flow from "what is this" to "what to do next", combining deterministic analyzer results, vibe coding insights (when detected), and AI narrative interpretation.

#### Scenario: 4 또는 5개 섹션이 결과에 포함됨
- **WHEN** 유효한 레포 경로가 분석되고 바이브코딩이 *감지되면*
- **THEN** briefing 결과는 다섯 섹션을 포함한다: 정체(what), 구조(how built), 현재 상태(current), 바이브코딩 인사이트(vibe), 다음 행동(next)

- **WHEN** 유효한 레포 경로가 분석되고 바이브코딩이 *감지되지 않으면*
- **THEN** briefing 결과는 네 섹션만 포함한다: 정체(what), 구조(how built), 현재 상태(current), 다음 행동(next). 바이브코딩 섹션의 페이로드는 부재 또는 null

#### Scenario: 섹션 데이터 결합
- **WHEN** briefing 결과가 빌드되면
- **THEN** 각 섹션은 결정론적 분석기(inventory, graph, metrics, entrypoints, quality, hotspots, summary, vibe-coding report)와 git history 데이터를 근거로 채워진다

#### Scenario: 바이브코딩 섹션은 인사이트 모듈로부터 채움
- **WHEN** briefing 결과의 바이브코딩 섹션이 빌드되면
- **THEN** 그 데이터는 (감지된 경우에만) vibe-coding-insights capability에서 정의된 구조(자동 판별, 3축 상태, 타임라인, 행동+왜)를 포함한다. 비감지 시 섹션 페이로드는 부재 또는 null

### Requirement: 다음 행동 카테고리 분류
The system SHALL categorize each next-action recommendation into one of three buckets — `code`, `structural`, or `vibe_coding` — so the user can quickly identify what kind of action a recommendation is.

#### Scenario: 카테고리 필드 존재
- **WHEN** briefing 결과의 `next_actions` 항목이 직렬화되면
- **THEN** 각 항목은 `category` 필드를 포함하며 값은 `code`, `structural`, `vibe_coding` 중 하나이다

#### Scenario: AI 가 code/structural 카테고리 분류
- **WHEN** AI 해석이 다음 행동을 생성하면
- **THEN** AI 는 `code`(코드 측면 — 함수/모듈 단위의 변경, 테스트 보강, 에러 처리)와 `structural`(구조 측면 — 모듈 분리, 의존성 정리, 아키텍처) 두 카테고리로 직접 분류해서 반환한다

#### Scenario: vibe_coding 카테고리는 vibe_insights 에서 합성 — 감지 시에만
- **WHEN** briefing payload 가 빌드되고 vibe coding 이 *감지된 경우*
- **THEN** `vibe_coding` 카테고리 항목은 AI 가 직접 생성하지 않고 `vibe_insights.next_actions` 의 항목을 `category="vibe_coding"` 으로 표시해 평면 리스트에 합쳐진다

- **WHEN** briefing payload 가 빌드되고 vibe coding 이 *감지되지 않은 경우*
- **THEN** `vibe_coding` 카테고리 카드는 *생성되지 않는다*. 평면 리스트는 `code` / `structural` 카드만 포함한다

#### Scenario: 카테고리 누락 시 fallback
- **WHEN** AI 응답에서 항목의 `category` 필드가 누락되거나 허용된 값이 아니면
- **THEN** 시스템은 해당 항목의 카테고리를 `code` 로 강제한다

#### Scenario: 카테고리당 항목 수 제한
- **WHEN** 다음 행동이 직렬화되면
- **THEN** 각 카테고리는 최대 3개 항목을 가지며 카테고리가 비어있어도 (0개) 허용된다

### Requirement: AI 해석 결과 구조
The system SHALL parse and validate AI interpretation results with the new schema (axis state + blind_spots + process_proxies + 4-level state per axis, with vibe insights payload absent when not detected).

#### Scenario: AI 해석 결과 구조 — SCHEMA_VERSION 7
- **WHEN** AI 호출이 성공하고 결과가 직렬화되면
- **THEN** 결과는 `schema_version: 7` 을 포함하고, 바이브코딩 감지 시 vibe coding 섹션은 새 3 축(`intent / verification / continuity`)의 상태(`strong / moderate / weak / unknown`) + 신호 개수 + 대표 근거 + `blind_spots` + `process_proxies` 를 분리해 포함한다. 비감지 시 vibe coding 섹션은 *부재 또는 null* 이다

#### Scenario: 카테고리 필드 유지
- **WHEN** next_actions 가 직렬화되면
- **THEN** 각 항목은 여전히 `category` 필드를 포함하며 값은 `code`, `structural`, `vibe_coding` 중 하나이다 (직전 변경 동작 유지). vibe_coding 카테고리는 시스템이 vibe_insights 데이터에서 합성하며 비감지 시 합성하지 않는다.

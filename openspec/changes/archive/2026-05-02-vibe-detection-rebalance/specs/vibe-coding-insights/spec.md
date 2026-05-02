## MODIFIED Requirements

### Requirement: 바이브코딩 자동 판별
The system SHALL automatically determine whether a repository was built using vibe coding (AI-assisted development) based on weighted signals from files, git history, and documentation. When vibe coding is *not* detected, the system SHALL return *no vibe insights payload at all* (the field is absent or null in serialized output) — neither a "전통 방식" classification nor a starter guide is produced.

#### Scenario: 강한 신호로 감지
- **WHEN** 레포에 `CLAUDE.md`, `AGENTS.md`, `.claude/`, `.omc/`, `openspec/` 중 하나라도 존재하거나 git 커밋에 `Co-Authored-By: Claude` 패턴이 있으면
- **THEN** 시스템은 바이브코딩으로 분류한다

#### Scenario: 중간 신호로 감지
- **WHEN** 강한 신호는 없지만 `docs/validation/`, `docs/vibe-coding/`, conventional commit 형식 + 한국어 혼재 등 중간 신호가 2개 이상 있으면
- **THEN** 시스템은 바이브코딩으로 분류한다

#### Scenario: 약한 신호만 있을 때
- **WHEN** README의 Claude/GPT/Cursor 언급 같은 약한 신호만 있으면
- **THEN** 시스템은 바이브코딩으로 분류하지 않는다

#### Scenario: 미감지 — vibe insights 페이로드 부재
- **WHEN** 바이브코딩 신호가 임계 미만이면
- **THEN** 시스템은 vibe insights 페이로드를 *생성하지 않는다*. `build_vibe_insights` 는 `None` 을 반환하고, briefing 페이로드의 `vibe_insights` 필드는 *부재* 또는 `null` 로 직렬화된다. 시작 가이드 / "전통 방식" 분류 / blind_spots / process_proxies 어떤 필드도 제공되지 않는다

### Requirement: 결정론적 직렬화
The system SHALL serialize vibe coding insights deterministically so the same inputs produce identical bytes. The serialization SHALL include the new axis structure, blind spot field, and process proxies field. When vibe coding is not detected, *no insights payload is emitted at all*.

#### Scenario: 동일 결과
- **WHEN** 동일한 레포 상태에서 두 번 평가하면
- **THEN** 결정론적 부분(축 신호·상태, 타임라인 데이터, blind_spots, process_proxies) 의 직렬화 결과는 byte-identical 이다

#### Scenario: AI 부분 분리
- **WHEN** 결과가 직렬화되면
- **THEN** AI 종합 서술은 별도 필드에 분리되어 결정론적 부분과 구분된다

#### Scenario: 새 SCHEMA_VERSION
- **WHEN** 결과가 직렬화되면
- **THEN** schema_version 은 7 이며 (직전 6 에서 bump), 비감지 시 페이로드 부재 + starter_guide 제거를 반영한다

#### Scenario: 비감지 직렬화
- **WHEN** 바이브코딩이 감지되지 않은 레포에 대해 직렬화가 실행되면
- **THEN** vibe insights 응답 자체가 생성되지 않으며 (None), starter_guide 같은 어떤 보조 필드도 직렬화되지 않는다

## REMOVED Requirements

### Requirement: 바이브코딩 미감지 시 시작 가이드
**Reason**: `vibe-detection-rebalance` 변경 (옵션 A' 채택) 으로 비감지 프로젝트에 시작 가이드를 강제 노출하는 동작이 제거됨. 비감지 프로젝트 사용자(예: fastapi 분석가) 에게 "CLAUDE.md 작성하세요" 같은 권유는 부적절하다는 사용자 결정에 따름.
**Migration**: 기존 호출자에서 `vibe_insights.detected === false` 분기로 starter_guide 를 사용하던 코드는 제거. vibe_insights 가 *부재 또는 null* 인 경우를 처리하도록 변경. vibe coding 처음 시작하는 사용자를 위한 안내는 README 또는 외부 자료 (Anthropic Best Practices, OpenAI AGENTS.md guide) 링크로 별도 변경에서 처리.

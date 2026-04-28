## ADDED Requirements

### Requirement: AI 해석 레이어
The system SHALL package all deterministic analysis evidence and pass it to the Claude/Codex CLI adapter to generate a comprehensive AI interpretation of the codebase.

#### Scenario: 종합 증거 번들 생성
- **WHEN** briefing 분석이 실행되면
- **THEN** 시스템은 inventory, graph, metrics, quality, hotspots의 핵심 수치를 하나의 JSON 번들로 묶는다

#### Scenario: AI 해석 호출
- **WHEN** 증거 번들이 준비되면
- **THEN** 시스템은 기존 insights AI 어댑터(claude 또는 codex CLI)를 통해 종합 한국어 분석을 요청한다

#### Scenario: AI 해석 결과 구조
- **WHEN** AI 호출이 성공하면
- **THEN** 결과는 executive summary, architecture 설명, quality 평가, 상위 위험, 다음 행동 항목을 포함한다

#### Scenario: AI 미사용 시 결정론적 폴백
- **WHEN** AI 어댑터가 사용 불가능하거나 호출이 실패하면
- **THEN** 시스템은 AI 해석 없이 기존 결정론적 briefing 데이터를 반환하고 폴백 플래그를 포함한다

### Requirement: AI 해석 캐싱
The system SHALL cache AI interpretation results to avoid redundant calls for the same codebase state.

#### Scenario: 캐시 hit
- **WHEN** 동일 path와 동일 분석 데이터 hash에 대한 AI 해석 캐시가 존재하면
- **THEN** 시스템은 AI 어댑터를 호출하지 않고 캐시된 해석을 반환한다

#### Scenario: 캐시 저장
- **WHEN** AI 해석이 성공하면
- **THEN** 시스템은 결과를 `~/.cache/codexray/ai-briefing/<sha256_key>.json`에 저장한다

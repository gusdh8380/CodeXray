## MODIFIED Requirements

### Requirement: Briefing composition
The system SHALL build a codebase briefing model composed of five top-level sections that flow from "what is this" to "what to do next", combining deterministic analyzer results, vibe coding insights, and AI narrative interpretation.

#### Scenario: 5개 섹션이 결과에 포함됨
- **WHEN** 유효한 레포 경로가 분석되면
- **THEN** briefing 결과는 다섯 섹션을 포함한다: 정체(what), 구조(how built), 현재 상태(current), 바이브코딩 인사이트(vibe), 다음 행동(next)

#### Scenario: 섹션 데이터 결합
- **WHEN** briefing 결과가 빌드되면
- **THEN** 각 섹션은 결정론적 분석기(inventory, graph, metrics, entrypoints, quality, hotspots, summary, vibe-coding report)와 git history 데이터를 근거로 채워진다

#### Scenario: 바이브코딩 섹션은 인사이트 모듈로부터 채움
- **WHEN** briefing 결과의 바이브코딩 섹션이 빌드되면
- **THEN** 그 데이터는 vibe-coding-insights capability에서 정의된 구조(자동 판별, 3축 점수, 타임라인, 행동+왜)를 그대로 포함한다

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
- **THEN** 결과는 다섯 섹션 별 서술 텍스트를 포함하고 다음 행동 항목은 행동+왜+증거 형식이다

#### Scenario: AI 미사용 시 결정론적 폴백
- **WHEN** AI 어댑터가 사용 불가능하거나 호출이 실패하면
- **THEN** 시스템은 결정론적 템플릿 서술을 사용하고 폴백 플래그를 포함한다

### Requirement: AI 해석 캐싱
The system SHALL cache AI interpretation results to avoid redundant calls for the same repository state.

#### Scenario: 캐시 hit
- **WHEN** 동일 path와 동일 raw code bundle hash에 대한 캐시가 존재하면
- **THEN** 시스템은 AI 어댑터를 호출하지 않고 캐시된 해석을 반환한다

#### Scenario: 캐시 저장
- **WHEN** AI 해석이 성공하면
- **THEN** 시스템은 결과를 `~/.cache/codexray/ai-briefing/<sha256_key>.json`에 저장한다

#### Scenario: prompt version 무효화
- **WHEN** AI 프롬프트 버전이 올라간 후 분석을 실행하면
- **THEN** 시스템은 이전 버전 캐시를 무시하고 새 호출을 시작한다

### Requirement: Plain-language technical translation
The system SHALL translate structural and quality signals into plain Korean language suitable for non-developers in every Briefing section.

#### Scenario: 구조 평어 번역
- **WHEN** "어떻게 만들어졌나" 섹션이 표시되면
- **THEN** 서술은 graph, fan-in, SCC 같은 용어 없이 "중심 파일 하나가 시스템 전체를 붙잡고 있다" 같은 평어로 구조를 설명한다

#### Scenario: 품질 평어 번역
- **WHEN** "지금 상태" 섹션이 표시되면
- **THEN** 서술은 grade와 hotspot count의 실용적 함의를 메트릭 용어 없이 설명한다

### Requirement: Deep-dive preservation
The system SHALL preserve access to detailed analyzer outputs from each Briefing section.

#### Scenario: 섹션별 미시 탭 참조
- **WHEN** Briefing 섹션이 렌더링되면
- **THEN** 각 섹션은 관련된 미시 분석 탭(Quality, Hotspots, Graph, Inventory, Metrics, Entrypoints, Report, Vibe Coding)으로의 참조를 포함한다

### Requirement: Deterministic briefing serialization
The system SHALL serialize briefing data with `schema_version: 2`, deterministic ordering, and root-relative POSIX paths where paths are present.

#### Scenario: schema_version 변경
- **WHEN** briefing 결과가 직렬화되면
- **THEN** 결과의 schema_version 필드는 `2` 이고 5개 섹션 구조를 반영한다

#### Scenario: 결정론적 부분 반복 가능
- **WHEN** 동일 레포 상태로 두 번 분석하면
- **THEN** 결정론적 부분(섹션 데이터, 메트릭, 타임라인)의 직렬화 결과는 byte-identical이며 AI 서술은 별도 캐시 키로 관리된다

### Requirement: Briefing performance budget
The system SHALL complete the deterministic portion of briefing analysis within 5 seconds on the validation codebases. AI interpretation MAY take up to 90 seconds and SHALL stream progress updates.

#### Scenario: 결정론적 분석 시간
- **WHEN** CodeXray 또는 aquaview 레포를 분석하면
- **THEN** 결정론적 분석 단계(파일 수집, 메트릭, 타임라인 데이터)는 5초 내 완료되고 진행 상태가 사용자에게 보고된다

#### Scenario: AI 단계 진행 보고
- **WHEN** AI 해석 단계가 시작되면
- **THEN** 진행 상태는 적어도 시작과 완료 두 시점에 갱신되어 클라이언트에 전달된다

## REMOVED Requirements

### Requirement: Briefing presentation slides
**Reason:** PPT 슬라이드 데이터 모델은 화면에 제대로 노출되지 않았고 5개 섹션 구조로 흡수됨. 슬라이드의 핵심 의도(매크로 방향 잡기)는 react-frontend의 Briefing 5섹션 화면이 대체.

**Migration:** 클라이언트 코드는 더 이상 `presentation_slides` 필드를 사용하지 않는다. 대신 `briefing.sections` 배열을 사용한다 (codebase-briefing의 새 Briefing composition 요구 참조).

### Requirement: Presentation serialization
**Reason:** presentation_slides 필드 제거에 따라 직렬화 요구도 폐기.

**Migration:** schema_version이 2로 올라갔고 섹션 직렬화 요구가 새 Deterministic briefing serialization 요구로 대체됨.

### Requirement: Presentation depth preservation
**Reason:** 슬라이드 단위가 아닌 섹션 단위로 deep-dive 참조가 재정의됨.

**Migration:** Deep-dive preservation 요구의 새 섹션별 참조 시나리오를 사용한다.

### Requirement: Deep briefing interpretation
**Reason:** 슬라이드별 summary/meaning/risk/action 필드는 5개 섹션의 AI 서술과 행동+왜+증거 형식으로 재구성됨.

**Migration:** AI 해석 레이어 요구의 새 시나리오와 vibe-coding-insights의 행동+왜+증거 형식을 사용한다.

### Requirement: Creation story analysis
**Reason:** 창작 과정 해석은 vibe-coding-insights capability의 타임라인 데이터와 AI 종합 서술로 이동됨.

**Migration:** vibe-coding-insights 의 "개발 과정 타임라인 데이터"와 "AI 해석 통합" 요구를 참조.

### Requirement: Briefing 자동 랜딩 시작
**Reason:** SPA 도입과 자동 분석 흐름은 react-frontend capability의 "SPA 진입과 자동 분석" 요구로 이전됨.

**Migration:** react-frontend 의 새 요구를 사용한다.

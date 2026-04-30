# codebase-briefing Specification

## Purpose
The codebase-briefing capability composes CodeXray's deterministic analyzers into a presentation-like repository briefing that explains what the codebase is, its current status, how it was built, key risks, and next actions. It combines inventory, graph, metrics, entrypoints, quality, hotspots, summary, vibe-coding evidence, and git-history creation-process analysis, then feeds the web UI Briefing experience while preserving deep-dive access to the underlying analyzers.
## Requirements
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

### Requirement: Git-history creation process analysis
The system SHALL analyze git history as evidence for how the repository was created, especially from a vibe-coding workflow perspective.

#### Scenario: Git timeline available
- **WHEN** the target path is inside a git repository
- **THEN** the briefing includes commit count, recent commit messages, commit type distribution, and a creation-process timeline summary

#### Scenario: Vibe-coding process commits detected
- **WHEN** git history contains commits or changed paths for OpenSpec, validation documents, retrospectives, handoff documents, `AGENTS.md`, `CLAUDE.md`, `.omc`, `.roboco`, or `.claude`
- **THEN** the briefing classifies those commits as vibe-coding process evidence and cites the commit hash, message, and path category

#### Scenario: Git history unavailable
- **WHEN** the target path is not inside a git repository or git history cannot be read within the timeout
- **THEN** the briefing still returns successfully and marks creation history as unavailable

### Requirement: Presentation-like narrative
The system SHALL produce briefing text that can be read like a developer-prepared analysis deck while retaining evidence links.

#### Scenario: Shareable team summary
- **WHEN** the briefing renders the executive section
- **THEN** it includes a concise team-shareable explanation of what the repository appears to be, current status, strongest evidence, top risk, and next action

#### Scenario: Non-developer explanation
- **WHEN** the briefing renders the explanation section
- **THEN** it describes the repository in plain language without requiring knowledge of graph, fan-in, SCC, or hotspot terminology

### Requirement: Deep-dive preservation
The system SHALL preserve access to detailed analyzer outputs from each Briefing section.

#### Scenario: 섹션별 미시 탭 참조
- **WHEN** Briefing 섹션이 렌더링되면
- **THEN** 각 섹션은 관련된 미시 분석 탭(Quality, Hotspots, Graph, Inventory, Metrics, Entrypoints, Report, Vibe Coding)으로의 참조를 포함한다

### Requirement: Deterministic briefing serialization
The system SHALL serialize briefing data with `schema_version: 3`, deterministic ordering, and root-relative POSIX paths where paths are present.

#### Scenario: schema_version 변경
- **WHEN** briefing 결과가 직렬화되면
- **THEN** 결과의 schema_version 필드는 `3` 이고 5개 섹션 + 카테고리 분류된 next_actions 구조를 반영한다

#### Scenario: 결정론적 부분 반복 가능
- **WHEN** 동일 레포 상태로 두 번 분석하면
- **THEN** 결정론적 부분(섹션 데이터, 메트릭, 타임라인, vibe_coding 카테고리 항목)의 직렬화 결과는 byte-identical이며 AI 서술은 별도 캐시 키로 관리된다

### Requirement: Briefing performance budget
The system SHALL complete the deterministic portion of briefing analysis within 5 seconds on the validation codebases. AI interpretation MAY take up to 90 seconds and SHALL stream progress updates.

#### Scenario: 결정론적 분석 시간
- **WHEN** CodeXray 또는 aquaview 레포를 분석하면
- **THEN** 결정론적 분석 단계(파일 수집, 메트릭, 타임라인 데이터)는 5초 내 완료되고 진행 상태가 사용자에게 보고된다

#### Scenario: AI 단계 진행 보고
- **WHEN** AI 해석 단계가 시작되면
- **THEN** 진행 상태는 적어도 시작과 완료 두 시점에 갱신되어 클라이언트에 전달된다

### Requirement: Plain-language technical translation
The system SHALL translate structural and quality signals into plain Korean language suitable for non-developers in every Briefing section.

#### Scenario: 구조 평어 번역
- **WHEN** "어떻게 만들어졌나" 섹션이 표시되면
- **THEN** 서술은 graph, fan-in, SCC 같은 용어 없이 "중심 파일 하나가 시스템 전체를 붙잡고 있다" 같은 평어로 구조를 설명한다

#### Scenario: 품질 평어 번역
- **WHEN** "지금 상태" 섹션이 표시되면
- **THEN** 서술은 grade와 hotspot count의 실용적 함의를 메트릭 용어 없이 설명한다

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


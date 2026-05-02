# codebase-briefing Specification

## Purpose
The codebase-briefing capability composes CodeXray's deterministic analyzers into a presentation-like repository briefing that explains what the codebase is, its current status, how it was built, key risks, and next actions. It combines inventory, graph, metrics, entrypoints, quality, hotspots, summary, vibe-coding evidence, and git-history creation-process analysis, then feeds the web UI Briefing experience while preserving deep-dive access to the underlying analyzers.
## Requirements
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
The system SHALL translate structural and quality signals into plain Korean language suitable for non-developers in every Briefing-area section. The Briefing area's audience is exclusively non-developer vibe coders; senior developers seeking depth read the Detailed Analysis toggle instead.

#### Scenario: 구조 평어 번역
- **WHEN** "어떻게 만들어졌나" 섹션이 표시되면
- **THEN** 서술은 graph, fan-in, SCC 같은 용어 없이 "중심 파일 하나가 시스템 전체를 붙잡고 있다" 같은 평어로 구조를 설명한다

#### Scenario: 품질 평어 번역
- **WHEN** "지금 상태" 섹션이 표시되면
- **THEN** 서술은 grade 와 hotspot count 의 실용적 함의를 메트릭 용어 없이 설명한다

#### Scenario: 브리핑 영역의 청자는 비개발자 100%
- **WHEN** Briefing 영역의 모든 텍스트(executive, architecture, quality_risk, key_insight, intent_alignment, next_actions, vibe coding section, 검토 경고 배너)가 생성되면
- **THEN** 텍스트는 "coupling", "fan-in", "fan-out", "DAG", "SCC", "p90", "hotspot priority" 같은 메트릭/그래프 용어를 직접 사용하지 않는다. 등급(A/B/C/D/F)과 파일 경로는 인용해도 되지만 그 의미를 평어로 함께 풀어 써야 한다

#### Scenario: 검토 경고 배너 톤
- **WHEN** Next Actions 영역의 검토 경고 배너가 렌더링되면
- **THEN** 배너 본문은 메트릭 용어 없이 "AI 추천이라 부적절할 수 있다" 와 "특정 파일은 원래 자주 바뀌는 게 정상일 수 있다" 의미를 비개발자 친화적 표현으로 전달한다

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

### Requirement: Next action AI 프롬프트 3단 구조
The system SHALL ensure that every non-empty `ai_prompt` value in the briefing payload's `next_actions` follows a 3-stage structure that a non-developer vibe coder can paste verbatim into a fresh AI session, regardless of whether the item was generated by the AI adapter (`code` / `structural` categories) or by the deterministic synthesizer (`vibe_coding` category, fallback hotspot/grade cards). The label set is the v7-realign version.

#### Scenario: 6 라벨 텍스트 형식 — v7
- **WHEN** `ai_prompt` 가 비어있지 않은 상태로 직렬화되면
- **THEN** 텍스트는 최소 세 라벨(`[현재 프로젝트]`, `[해줄 일]`, `[성공 기준과 직접 확인 방법]`)을 포함하며, 옵션 라벨(`[이번 변경의 이유]`, `[작업 전 읽을 것]`, `[건드리지 말 것]`)도 같은 대괄호 형식을 따른다

#### Scenario: 자족적 컨텍스트
- **WHEN** ai_prompt 가 생성되면
- **THEN** `[현재 프로젝트]` 섹션은 새 AI 세션이 이 레포를 모른다고 가정하고 한두 줄 요약을 포함한다 (CodeXray 분석 결과 인용 OK)

#### Scenario: 동기 (이번 변경의 이유)
- **WHEN** ai_prompt 가 생성되면
- **THEN** `[이번 변경의 이유]` 옵션 섹션이 채워질 경우, evidence 를 평어로 풀어 *왜* 이 작업이 지금 필요한지를 한두 문장으로 명시한다

#### Scenario: 성공 기준과 검증
- **WHEN** ai_prompt 가 생성되면
- **THEN** `[성공 기준과 직접 확인 방법]` 섹션은 (1) 작업이 *끝났다고 판단할 수 있는 객관 기준* (파일 존재, 명령 실행 결과, 화면 동작 등) 1 개 이상 + (2) 비개발자가 코드를 안 보고도 회귀 여부를 확인할 수 있는 *직접 확인 절차* 1 개 이상을 포함한다

#### Scenario: AI 응답이 형식을 깨뜨릴 때 폴백
- **WHEN** AI 응답의 `ai_prompt` 가 v7 필수 라벨 셋(`[현재 프로젝트]`, `[해줄 일]`, `[성공 기준과 직접 확인 방법]`) 중 하나라도 결손이면
- **THEN** 시스템은 결정론적 템플릿으로 ai_prompt 를 교체한다

#### Scenario: 빈 ai_prompt 허용
- **WHEN** AI 응답이 `ai_prompt` 를 누락하거나 빈 문자열로 반환하면
- **THEN** 시스템은 빈 문자열을 그대로 보존하고 3단 규칙을 적용하지 않는다 (프론트엔드는 빈 prompt 카드 영역을 숨긴다)

#### Scenario: prompt version bump
- **WHEN** ai_prompt 형식 규칙이 v6-persona-split 에서 v7-realign 으로 변경 적용되면
- **THEN** `PROMPT_VERSION` 값이 `v7-realign` 으로 갱신되어 기존 캐시가 자동 무효화된다

### Requirement: 카드 수 동적 정책
The Briefing payload's next_actions list SHALL contain 0 to 3 cards based on a leverage-based policy, *not* a forced count of 3 per category. The default is 1 card.

#### Scenario: 0개 카드 — 고확신 액션 없음
- **WHEN** AI 와 결정론적 합성 둘 다에서 고확신 다음 행동을 생성하지 못했을 때
- **THEN** payload 의 `next_actions` 는 빈 리스트이고, 별도 필드 `praise` 또는 `judgment_pending` 또는 `silent` 중 하나로 0 개 상태가 분기된다 (vibe-coding-insights 의 "침묵 / 칭찬 / 판단 보류 분리" 요구사항을 따른다)

#### Scenario: 1개 카드 — 기본값
- **WHEN** 가장 큰 병목 1 개가 두 개 이상의 결손 신호를 동시에 해결할 수 있을 때
- **THEN** payload 의 `next_actions` 는 그 1 개만 포함한다

#### Scenario: 2-3개 카드 — 독립 고확신 병목
- **WHEN** 서로 독립적이고 고확신인 병목이 2 개 또는 3 개 있을 때
- **THEN** payload 의 `next_actions` 는 그 만큼의 카드를 포함한다 (최대 3 개)

#### Scenario: 카테고리당 최대 3개 제한 폐지
- **WHEN** 카드들이 카테고리(`code` / `structural` / `vibe_coding`) 로 분류될 때
- **THEN** 시스템은 카테고리당 강제 3 개 채움 정책을 적용하지 않으며, 한 카테고리에서 0 ~ 3 개가 모두 허용된다 (전체 카드 수 0–3 한도 내에서)

### Requirement: blind spot 상시 노출
The Briefing area SHALL always display a "이 도구가 못 본 것" block that lists the dimensions the tool cannot judge from code alone, regardless of analysis results.

#### Scenario: blind spot 블록 고정 노출
- **WHEN** Briefing 화면이 렌더링되면
- **THEN** 화면의 검토 경고 배너 *바로 아래* 또는 vibe coding 섹션 *하단* 에 고정 블록이 표시되고, 다음 4 항목을 최소한 포함한다:
  1. 사용자(나)가 What/Why/Next 를 자기 입으로 설명할 수 있는가
  2. 손으로 한 검증이 *실제로 매번* 굴러가는가
  3. 다음 행동의 우선순위를 사람이 정하고 있는가
  4. 외부 도구(Notion, Confluence, Slack, Linear 등)에 있는 의도·결정 흔적과 README 같은 문서의 *질적 깊이* 는 자동 판단 못 합니다

#### Scenario: blind spot 블록 톤
- **WHEN** blind spot 블록이 렌더링되면
- **THEN** 본문은 *자가 점검 체크리스트* 톤을 따른다 ("이 셋은 코드만 봐서는 판단 못 합니다. 화면 상태와 무관하게 자가 점검해 주세요"). "이 도구가 못 미덥다" 는 인상이 아니라 *사용자 책임을 환기* 하는 어조.

### Requirement: AI 해석 결과 구조
The system SHALL parse and validate AI interpretation results with the new schema (axis state + blind_spots + process_proxies + 4-level state per axis, with vibe insights payload absent when not detected).

#### Scenario: AI 해석 결과 구조 — SCHEMA_VERSION 7
- **WHEN** AI 호출이 성공하고 결과가 직렬화되면
- **THEN** 결과는 `schema_version: 7` 을 포함하고, 바이브코딩 감지 시 vibe coding 섹션은 새 3 축(`intent / verification / continuity`)의 상태(`strong / moderate / weak / unknown`) + 신호 개수 + 대표 근거 + `blind_spots` + `process_proxies` 를 분리해 포함한다. 비감지 시 vibe coding 섹션은 *부재 또는 null* 이다

#### Scenario: 카테고리 필드 유지
- **WHEN** next_actions 가 직렬화되면
- **THEN** 각 항목은 여전히 `category` 필드를 포함하며 값은 `code`, `structural`, `vibe_coding` 중 하나이다 (직전 변경 동작 유지). vibe_coding 카테고리는 시스템이 vibe_insights 데이터에서 합성하며 비감지 시 합성하지 않는다.


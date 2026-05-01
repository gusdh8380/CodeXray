# vibe-coding-insights Specification

## Purpose
The vibe-coding-insights capability automatically detects whether a repository was built using vibe coding (AI-assisted development), evaluates its vibe coding quality on three independent axes (environment setup, development process cleanliness, handover readiness), reconstructs a process timeline from git history, and produces action+reason+evidence next-step recommendations. When vibe coding is not detected, it provides a concrete starter guide. Results feed the Briefing's vibe coding section and the standalone Vibe Coding micro-tab.
## Requirements
### Requirement: 바이브코딩 자동 판별
The system SHALL automatically determine whether a repository was built using vibe coding (AI-assisted development) based on weighted signals from files, git history, and documentation.

#### Scenario: 강한 신호로 감지
- **WHEN** 레포에 `CLAUDE.md`, `AGENTS.md`, `.claude/`, `.omc/`, `openspec/` 중 하나라도 존재하거나 git 커밋에 `Co-Authored-By: Claude` 패턴이 있으면
- **THEN** 시스템은 바이브코딩으로 분류한다

#### Scenario: 중간 신호로 감지
- **WHEN** 강한 신호는 없지만 `docs/validation/`, `docs/vibe-coding/`, conventional commit 형식 + 한국어 혼재 등 중간 신호가 2개 이상 있으면
- **THEN** 시스템은 바이브코딩으로 분류한다

#### Scenario: 약한 신호만 있을 때
- **WHEN** README의 Claude/GPT/Cursor 언급 같은 약한 신호만 있으면
- **THEN** 시스템은 바이브코딩으로 분류하지 않는다

#### Scenario: 미감지
- **WHEN** 바이브코딩 신호가 임계 미만이면
- **THEN** 시스템은 "전통 방식" 분류로 응답하고 시작 가이드를 위한 데이터를 함께 반환한다

### Requirement: 3축 진단 평가
The system SHALL evaluate vibe coding quality on three axes — `intent` (의도), `verification` (검증), `continuity` (이어받기) — when vibe coding is detected. Each axis SHALL be presented as a 4-level state (`strong / moderate / weak / unknown`) with the count of recognized signals and 2–3 representative pieces of evidence, not as a 0–100 numeric score visible to the user.

#### Scenario: intent 축 평가
- **WHEN** 바이브코딩이 감지된 레포를 평가하면
- **THEN** 시스템은 intent 축의 상태를 (a) AI 지속 지시 문서 1종 이상 존재 + 충실도 충족, (b) 프로젝트 의도 문서 1종 이상 존재, (c) 의도와 비의도 명문화 — 셋의 충족도로 결정한다. *구체 파일/패턴 매칭은 design.md Decision 1 의 broadened 풀을 따른다.*

#### Scenario: verification 축 평가
- **WHEN** 바이브코딩이 감지된 레포를 평가하면
- **THEN** 시스템은 verification 축의 상태를 (a) 손 검증 흔적 1종 이상 존재, (b) 자동 테스트와 CI 1종 이상 존재, (c) 재현 가능 실행 경로 1종 이상 존재 — 셋의 충족도로 결정한다. *구체 파일/패턴 매칭은 design.md Decision 1 의 broadened 풀을 따른다.*

#### Scenario: continuity 축 평가
- **WHEN** 바이브코딩이 감지된 레포를 평가하면
- **THEN** 시스템은 continuity 축의 상태를 (a) 작게 이어가기 흔적 (작은 PR + saved plans 등), (b) 학습 반영 흔적 (회고 + CHANGELOG + 지시 문서 갱신 등), (c) 핸드오프 문서 — 셋의 충족도로 결정한다. *구체 파일/패턴 매칭은 design.md Decision 1 의 broadened 풀을 따른다.*

#### Scenario: 4단계 상태 매핑
- **WHEN** 어떤 축의 신호 수집이 완료되면
- **THEN** 그 축은 다음 4 상태 중 하나로 표시된다: `strong` (인지된 신호 ≥ 4 그리고 핵심 신호 모두 충족), `moderate` (인지된 신호 ≥ 2), `weak` (인지된 신호 ≥ 1), `unknown` (데이터 수집 실패 또는 모든 측정 신호 미달). 임계값은 자기 적용 데이터에 따라 조정 가능.

#### Scenario: 사용자 노출 화면에 0-100 점수 미노출
- **WHEN** 결과가 SPA 화면에 렌더링되면
- **THEN** 각 축은 4 상태 라벨 + 인지된 신호 개수 + 대표 근거 2-3 개로 표시되고, 0-100 원시 점수는 *기본 노출되지 않는다* (디버그/실험 토글에서만 접근)

#### Scenario: 가장 약한 축 식별 — 동점 처리
- **WHEN** 3 축의 상태가 모두 `strong` 일 때
- **THEN** 시스템은 "가장 약한 축" 을 비워두고 (없음), 다음 행동 영역은 칭찬 또는 침묵 분기로 진입한다

- **WHEN** `weak` 또는 `moderate` 축이 둘 이상 동률일 때
- **THEN** 시스템은 그 중 하나를 정해진 우선순위(`intent > verification > continuity`)로 선택해 가장 약한 축으로 표시하고 그 사실을 보조 텍스트로 명시한다

### Requirement: 개발 과정 타임라인 데이터
The system SHALL produce timeline data that reconstructs how the repository was built from a vibe coding process perspective.

#### Scenario: 프로세스 단계 도입 시점
- **WHEN** git history가 사용 가능하면
- **THEN** 타임라인 데이터는 각 프로세스 단계(에이전트 지침 / 명세 / 검증 / 회고)가 처음 도입된 커밋과 시점을 포함한다

#### Scenario: 코드와 프로세스 비율
- **WHEN** 타임라인이 생성되면
- **THEN** 시간축을 따라 일정 구간마다 코드 커밋과 프로세스 커밋의 비율을 계산해서 포함한다

#### Scenario: git 미사용 시 폴백
- **WHEN** git history가 사용 불가능하면
- **THEN** 타임라인 데이터는 비어있음을 표시하고 파일 증거 기반의 단순 단계 체크를 대체로 제공한다

### Requirement: 행동+왜+증거 형식의 다음 행동
The system SHALL produce next process action recommendations as quadruples of `action`, `reason`, analysis `evidence`, and `ai_prompt`. The `ai_prompt` field is a non-developer-ready text that can be pasted into the next AI session as-is. The number of cards generated SHALL follow a leverage-based dynamic policy from 0 to 3 — *not* a forced count of 3.

#### Scenario: 행동 항목 구조
- **WHEN** 다음 행동이 생성되면
- **THEN** 각 항목은 `action`, `reason`, `evidence`, `ai_prompt` 네 필드를 모두 포함한다

#### Scenario: evidence는 분석 결과 인용
- **WHEN** 행동 항목의 evidence가 생성되면
- **THEN** evidence 필드는 분석에서 도출된 구체적 수치 또는 파일 경로를 포함한다 (예: "Hotspot 23개", "validation 디렉토리 0개", "GameManager.cs coupling 45")

#### Scenario: reason은 왜 그 행동인지 설명
- **WHEN** 행동 항목의 reason이 생성되면
- **THEN** reason 필드는 evidence와 action의 인과 관계를 한국어 한 문장으로 설명한다

#### Scenario: ai_prompt 6 라벨 — v7 라벨 셋
- **WHEN** 행동 항목의 `ai_prompt` 가 비어있지 않게 생성되면
- **THEN** ai_prompt 텍스트는 다음 6 라벨을 사용한다: `[현재 프로젝트]` / `[이번 변경의 이유]` / `[해줄 일]` / `[작업 전 읽을 것]` / `[성공 기준과 직접 확인 방법]` / `[건드리지 말 것]` 중에서, 그리고 codebase-briefing 의 "Next action AI 프롬프트 3단 구조" 요구사항 (필수 3 라벨 + 자족적 컨텍스트 + 검증 체크리스트) 을 따른다

#### Scenario: 카드 수 동적 정책
- **WHEN** 가장 큰 병목 1 개가 두 개 이상의 결손 신호를 동시에 해결할 수 있으면
- **THEN** 카드 1 개만 생성한다 (기본값)

- **WHEN** 서로 독립적인 고확신 병목이 2 개 있을 때
- **THEN** 카드 2 개를 생성한다

- **WHEN** 서로 겹치지 않는 고확신·저중복 액션이 3 개 있을 때
- **THEN** 카드 3 개를 생성한다 (최대)

- **WHEN** 고확신 액션이 0 개일 때
- **THEN** 카드 0 개를 생성하고 침묵·칭찬·판단 보류 분기를 따른다

#### Scenario: 레버리지 기반 합성
- **WHEN** 여러 결손 신호가 한 작업(예: `CLAUDE.md` 작성)으로 동시 해결 가능할 때
- **THEN** 시스템은 그 신호들을 *하나의 카드* 로 합성하여 카드 수를 늘리지 않는다

### Requirement: 바이브코딩 미감지 시 시작 가이드
The system SHALL provide a starter guide when vibe coding is not detected, recommending concrete first steps. Each starter item SHALL include an `ai_prompt` that follows the v7 6-label structure so the non-developer user can paste it directly into the next AI session.

#### Scenario: 시작 가이드 항목
- **WHEN** 레포가 바이브코딩 미감지로 분류되면
- **THEN** 결과는 "전통 방식. 바이브코딩 시작한다면 첫 걸음은?" 문구와 함께 첫 단계 추천 항목을 포함한다

#### Scenario: 추천 첫 단계
- **WHEN** 시작 가이드가 생성되면
- **THEN** 추천은 최소 `CLAUDE.md` 작성, 의도 문서화, 명세 도입을 포함하며 각 항목은 행동+왜+해당 레포의 현재 상태 인용 형식을 따른다

#### Scenario: 시작 가이드 ai_prompt — v7 라벨
- **WHEN** 시작 가이드 항목의 `ai_prompt` 가 생성되면
- **THEN** ai_prompt 텍스트는 codebase-briefing 의 "Next action AI 프롬프트 3단 구조" 요구사항 (필수 3 라벨: `[현재 프로젝트]`, `[해줄 일]`, `[성공 기준과 직접 확인 방법]`) 을 따른다

### Requirement: AI 해석 통합
The system SHALL synthesize the three-axis results, timeline data, and detection result into one Korean narrative paragraph using the AI adapter, using the new axis names (`intent / verification / continuity`).

#### Scenario: 종합 서술 생성
- **WHEN** 3 축 평가와 타임라인 데이터가 준비되면
- **THEN** 시스템은 AI 어댑터를 통해 약점 강조 서술 한 문단을 생성한다

#### Scenario: 서술은 새 3축 모두 언급
- **WHEN** AI 종합 서술이 반환되면
- **THEN** 서술은 의도(intent) / 검증(verification) / 이어받기(continuity) 세 축의 상태를 모두 한 번 이상 언급하고 가장 약한 축을 강조한다 (단, 3 축 모두 `strong` 인 경우에는 칭찬 톤으로 작성)

#### Scenario: AI 미사용 시 폴백
- **WHEN** AI 어댑터가 사용 불가능하면
- **THEN** 시스템은 결정론적 템플릿 서술을 사용하고 폴백 플래그를 포함한다

### Requirement: 결정론적 직렬화
The system SHALL serialize vibe coding insights deterministically so the same inputs produce identical bytes. The serialization SHALL include the new axis structure, blind spot field, and process proxies field.

#### Scenario: 동일 결과
- **WHEN** 동일한 레포 상태에서 두 번 평가하면
- **THEN** 결정론적 부분(축 신호·상태, 타임라인 데이터, 시작 가이드, blind_spots, process_proxies) 의 직렬화 결과는 byte-identical 이다

#### Scenario: AI 부분 분리
- **WHEN** 결과가 직렬화되면
- **THEN** AI 종합 서술은 별도 필드에 분리되어 결정론적 부분과 구분된다

#### Scenario: 새 SCHEMA_VERSION
- **WHEN** 결과가 직렬화되면
- **THEN** schema_version 은 6 이며 (직전 5 에서 bump), 4단계 상태 + blind_spots + process_proxies 분리를 반영한다

### Requirement: 8 운영 정의와 측정 가능성 분리
The system SHALL define vibe coding quality with eight operational signals, and explicitly separate the six that can be inferred from repository artifacts from the two that require user conversation or observation.

#### Scenario: 흔적 기반 6개 신호 정의 (원칙 수준)
- **WHEN** 시스템이 바이브코딩 평가를 수행하면
- **THEN** 다음 6개 신호를 흔적 기반(`evidence-based`) 측정 대상으로 사용한다 (각 신호의 *구체 파일·패턴 매칭은 design.md Decision 1 의 broadened 풀을 따른다*. 특정 도구·프로젝트 컨벤션을 표준처럼 강제하지 않는다):
  1. 의도가 글로 박혀 작동한다 — AI 지속 지시 문서가 *어떤 도구 표준이든* 1종 이상 존재하고 충실도 임계 충족
  2. 의도와 비의도가 먼저 적힌다 — 프로젝트 의도 문서 또는 decision log / ADR 등에 의도와 비의도가 명문화
  3. 손으로 검증한 흔적 — 검증 디렉토리·문서·screenshot·demo *어떤 형식이든* 존재
  4. 재현 가능한 실행 경로 — README 명령어 블록 / 패키지 매니페스트 scripts / Makefile 등 *어떤 형식이든* 존재
  5. 실패에서 배운 흔적이 다음 변경에 반영 — 회고 디렉토리 / CHANGELOG reasoning / 지시 문서 갱신 빈도 *어떤 형식이든*
  6. 작게 쪼개고 이어갈 수 있다 — 작은 PR/commit 빈도 / saved plans (TODO·ROADMAP·tasks 등) *어떤 형식이든*

#### Scenario: 대화·관찰 2개 신호 명시
- **WHEN** 시스템이 바이브코딩 평가를 수행하면
- **THEN** 다음 2개 신호는 흔적으로 측정하지 *않고*, 결과 payload 의 `blind_spots` 필드로 분리해 사용자에게 자가 점검 항목으로 노출한다:
  1. 사용자가 What/Why/Next 를 자기 입으로 설명할 수 있는가
  2. 다음 행동의 우선순위를 사람이 정하고 있는가

#### Scenario: 외부 도구 사각지대 명시
- **WHEN** blind_spots 필드가 직렬화되면
- **THEN** 위 2개 신호 외에 다음 한 줄을 *항상 함께* 포함한다: "외부 도구(Notion, Confluence, Slack, Linear 등)에 있는 의도·결정 흔적과 README 같은 문서의 *질적 깊이* 는 자동 판단 못 합니다."

#### Scenario: 신호 수집 결과 payload 분리
- **WHEN** 평가 결과가 직렬화되면
- **THEN** payload 는 흔적 기반 6개의 측정 결과를 `signals` 필드에, 사각지대 2개를 `blind_spots` 필드에 분리해 포함한다

### Requirement: 약점 vs 사각지대 분리 노출
The system SHALL distinguish "confirmed gaps from repository evidence" from "blind spots that the tool cannot judge", so the user understands which findings are tool-confirmed and which require self-assessment.

#### Scenario: 결손 vs 사각지대
- **WHEN** 어떤 신호가 흔적 6개 중 하나이고 그 신호가 *부재* 로 직접 확인되면
- **THEN** 시스템은 그것을 "코드에서 확인된 빈칸(`confirmed_gap`)" 으로 표기한다

- **WHEN** 어떤 항목이 사각지대 2개 중 하나일 때
- **THEN** 시스템은 그것을 "도구가 못 본 차원(`blind_spot`)" 으로 별도 표기하고 결손 카운트나 점수 산정에 합산하지 않는다

### Requirement: 약한 process proxy 강등
The system SHALL not use weak process proxies (feat/fix ratio, spec commit timing, hotspot accumulation rate, intent document update frequency) as standalone judgment evidence; these are exposed only as supplementary information.

#### Scenario: 약한 proxy 는 점수 계산에서 제외
- **WHEN** 시스템이 새 3축(`intent / verification / continuity`) 의 상태를 계산하면
- **THEN** feat/fix 비율, spec 커밋 시점 순서, hotspot 누적 속도, intent 문서 업데이트 빈도 같은 약한 proxy 는 *상태 결정에 직접 사용되지 않는다*

#### Scenario: 보조 정보 패널 노출
- **WHEN** payload 가 직렬화되면
- **THEN** 약한 proxy 들은 `process_proxies` 라는 별도 보조 필드에 정리되어 사용자가 *참고용* 으로 볼 수 있게 분리된다

### Requirement: 침묵 / 칭찬 / 판단 보류 분리
The system SHALL distinguish three zero-action states so the user understands whether silence means "all is well", "tool cannot judge", or genuinely no actionable signal.

#### Scenario: 칭찬 — 강한 긍정 신호 + 액션 0개
- **WHEN** 시스템이 다음 행동 0 개를 생성했고 강한 긍정 신호가 1 개 이상 있을 때
- **THEN** 시스템은 다음 행동 영역에 칭찬·유지 라인 1 개를 채운다 (예: "validation 문서가 매 변경마다 갱신되고 있습니다 — 이 습관을 유지하세요")

#### Scenario: 판단 보류 — 사각지대만 남음
- **WHEN** 시스템이 다음 행동 0 개를 생성했고 강한 긍정 신호 0 개이며 결손이 모두 사각지대(blind spot) 일 때
- **THEN** 시스템은 칭찬 라인을 생성하지 않고 "코드만 봐선 추가 진단 어려움 — 사용자 대화·시연이 필요합니다" 라는 판단 보류 라인을 채운다

#### Scenario: 침묵 — 위 둘 모두 해당 없음
- **WHEN** 시스템이 다음 행동 0 개를 생성했고 강한 긍정 신호 0 개이며 사각지대도 비어있을 때
- **THEN** 시스템은 다음 행동 영역에 별도 메시지를 채우지 않는다 (드문 케이스이며 빈도 측정 대상)

### Requirement: 외부 OSS 데이터셋 기반 임계값·신호 풀 검증 절차

The system's vibe coding 3-axis thresholds (`strong / moderate / weak / unknown`) and signal pools SHALL be validated against an external OSS dataset before any threshold or signal-pool change is committed. The dataset SHALL include at least 5 repositories chosen for diversity along three dimensions: language ecosystem, project age, and AI-tool adoption stage.

#### Scenario: 검증 데이터셋 다양성 매트릭스
- **WHEN** 외부 검증 데이터셋이 정의되면
- **THEN** 데이터셋은 최소 5 개 레포를 포함하고, 다음 세 차원에서 *각각 2 개 이상의 분포* 를 가진다: 언어 생태계 (예: JS / Python / Rust / C 중 2 개 이상), 프로젝트 연령 (신생 < 3 년 / 성숙 ≥ 3 년 각각 1 개 이상), AI 도구 도입 단계 (AI 지시 문서 있음 / 없음 / 부분 도입 중 2 개 이상)

#### Scenario: 검증 시 AI 호출 차단
- **WHEN** 외부 검증 절차가 실행되면
- **THEN** 결정론 분석 (`build_vibe_insights` 의 신호 수집 + 3 축 상태 + blind_spot + process_proxies) 만 수집되고, AI narrative 또는 AI 카드 합성 호출은 *수행되지 않는다*

#### Scenario: 검증 결과 문서 위치 고정
- **WHEN** 외부 검증이 완료되면
- **THEN** 결과는 `docs/validation/non-roboco-validation-results.md` 에 다음 항목을 포함하여 기록된다: (1) 레포별 3 축 상태 표, (2) 축별 신호 풀 ratio 분포, (3) 누락된 신호 사례, (4) 과탐지 사례, (5) 임계값·신호 풀 권고안, (6) 후속 변경 제안

#### Scenario: 검증 데이터 raw 보존
- **WHEN** 외부 검증이 실행되면
- **THEN** 각 레포의 vibe_insights payload 는 `docs/validation/non-roboco-data/{repo-name}.json` 에 결정론적 직렬화 형식 그대로 저장되어 재분석이 가능하다

### Requirement: 임계값·신호 풀 변경의 근거 트레일

Any change that modifies vibe coding 3-axis thresholds or signal pools SHALL cite a corresponding entry in `docs/validation/non-roboco-validation-results.md` (or a successor results document) as the data justification. Changes lacking such a citation SHALL be rejected at proposal review.

#### Scenario: 임계값 조정 변경의 근거 인용
- **WHEN** 새 OpenSpec 변경이 `strong / moderate / weak` 임계값 비율을 수정하려 할 때
- **THEN** 변경의 proposal.md 는 결과 문서의 해당 권고 섹션을 명시적으로 인용 (파일 경로 + 섹션 헤딩) 한다

#### Scenario: 신호 풀 확장의 근거 인용
- **WHEN** 새 OpenSpec 변경이 3 축의 신호 풀에 새 파일/패턴을 추가하려 할 때
- **THEN** 변경의 proposal.md 는 결과 문서의 "누락된 신호 사례" 섹션 또는 "권고안" 섹션을 명시적으로 인용한다

### Requirement: 검증 중 false positive 즉시 수정의 경계

External validation MAY apply a *narrow* code fix during the same change ONLY when all three of the following conditions hold simultaneously: (1) the issue is a clear, undisputed false positive identifiable by visual inspection, (2) the fix touches at most one function and at most a few lines, (3) the existing test suite remains green and self-application result does not regress. Any change that violates one or more of these conditions SHALL be deferred to a follow-up change.

#### Scenario: 즉시 수정이 허용되는 경우
- **WHEN** 검증 중 사람이 봐도 명백한 false positive 가 발견되고, 수정이 1 함수 1–수 줄 범위이며, 기존 테스트와 자기 적용 결과가 변하지 않을 때
- **THEN** 본 변경 안에서 코드 수정을 *허용한다*

#### Scenario: 즉시 수정이 거부되는 경우
- **WHEN** 검증 중 발견된 이슈가 임계값 비율 변경, 신호 풀에 새 파일/패턴 추가, 다축에 걸친 로직 변경 중 하나라도 해당될 때
- **THEN** 본 변경에서 코드는 수정하지 *않고*, 결과 문서의 "후속 변경 제안" 섹션에 기록한다


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
The system SHALL evaluate vibe coding quality on three independent axes when vibe coding is detected.

#### Scenario: 환경 구축 축 평가
- **WHEN** 바이브코딩이 감지된 레포를 평가하면
- **THEN** 시스템은 환경 구축 점수(0~100)를 `CLAUDE.md`, `AGENTS.md`, `.claude/settings`, `openspec/` 존재와 내용 충실도로 계산한다

#### Scenario: 개발 과정 깔끔함 축 평가
- **WHEN** 바이브코딩이 감지된 레포를 평가하면
- **THEN** 시스템은 개발 과정 점수를 git history 기반으로 계산한다 (feat 대비 fix 비율, 명세 커밋과 feat 커밋의 시간 순서, hotspot 누적 속도, intent 문서 업데이트 빈도)

#### Scenario: 이어받기 가능성 축 평가
- **WHEN** 바이브코딩이 감지된 레포를 평가하면
- **THEN** 시스템은 이어받기 점수를 검증 문서, 테스트 코드, 회고 문서, 인수인계 문서 존재 여부로 계산한다

#### Scenario: 축별 약점 식별
- **WHEN** 3축 평가가 완료되면
- **THEN** 결과는 가장 약한 축을 명시적으로 표시하고 그 축의 구체적 약점 항목 목록을 포함한다

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
The system SHALL produce next process action recommendations as triples of action, reason, and analysis evidence.

#### Scenario: 행동 항목 구조
- **WHEN** 다음 행동이 생성되면
- **THEN** 각 항목은 `action`, `reason`, `evidence` 세 필드를 모두 포함한다

#### Scenario: evidence는 분석 결과 인용
- **WHEN** 행동 항목의 evidence가 생성되면
- **THEN** evidence 필드는 분석에서 도출된 구체적 수치 또는 파일 경로를 포함한다 (예: "Hotspot 23개", "fix 비율 60%", "GameManager.cs coupling 45")

#### Scenario: reason은 왜 그 행동인지 설명
- **WHEN** 행동 항목의 reason이 생성되면
- **THEN** reason 필드는 evidence와 action의 인과 관계를 한국어 한 문장으로 설명한다

#### Scenario: 항목 수 제한
- **WHEN** 다음 행동이 생성되면
- **THEN** 항목 수는 최대 3개로 제한되고 우선순위 순으로 정렬된다

### Requirement: 바이브코딩 미감지 시 시작 가이드
The system SHALL provide a starter guide when vibe coding is not detected, recommending concrete first steps.

#### Scenario: 시작 가이드 항목
- **WHEN** 레포가 바이브코딩 미감지로 분류되면
- **THEN** 결과는 "전통 방식. 바이브코딩 시작한다면 첫 걸음은?" 문구와 함께 첫 단계 추천 항목을 포함한다

#### Scenario: 추천 첫 단계
- **WHEN** 시작 가이드가 생성되면
- **THEN** 추천은 최소 `CLAUDE.md` 작성, 의도 문서화, 명세 도입을 포함하며 각 항목은 행동+왜+해당 레포의 현재 상태 인용 형식을 따른다

### Requirement: AI 해석 통합
The system SHALL synthesize the three-axis scores, timeline data, and detection results into one Korean narrative paragraph using the AI adapter.

#### Scenario: 종합 서술 생성
- **WHEN** 3축 평가와 타임라인 데이터가 준비되면
- **THEN** 시스템은 AI 어댑터를 통해 약점 강조 서술 한 문단을 생성한다

#### Scenario: 서술은 3축 모두 언급
- **WHEN** AI 종합 서술이 반환되면
- **THEN** 서술은 환경 구축 / 개발 과정 / 이어받기 세 축의 상태를 모두 한 번 이상 언급하고 가장 약한 축을 강조한다

#### Scenario: AI 미사용 시 폴백
- **WHEN** AI 어댑터가 사용 불가능하면
- **THEN** 시스템은 결정론적 템플릿 서술을 사용하고 폴백 플래그를 포함한다

### Requirement: 결정론적 직렬화
The system SHALL serialize vibe coding insights deterministically so the same inputs produce identical bytes.

#### Scenario: 동일 결과
- **WHEN** 동일한 레포 상태에서 두 번 평가하면
- **THEN** 결정론적 부분(축 점수, 타임라인 데이터, 시작 가이드)의 직렬화 결과는 byte-identical 이다

#### Scenario: AI 부분 분리
- **WHEN** 결과가 직렬화되면
- **THEN** AI 종합 서술은 별도 필드에 분리되어 결정론적 부분과 구분된다

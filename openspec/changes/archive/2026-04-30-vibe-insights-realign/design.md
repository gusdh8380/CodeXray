## Context

직전 변경(`briefing-persona-split`)으로 페르소나 분리(위 = 비개발자 / 아래 = 개발자) + ai_prompt 6 라벨 골격이 박혔다. 그 직후 사용자가 두 가지 본질 문제를 제기:
- 점수가 우리 인지 패턴(특정 파일·커밋 패턴)에 묶여 있어 "더 좋은 환경"을 못 봄
- 카드 수 강제 매핑(약점 → 카드 3개)이 가짜 노이즈를 만듦

GPT Deep Research(2026-05-01)가 답을 운영 가능한 형태로 가져왔다. 핵심 권고:
- 한 줄 정의 → "외부화된 의도 / 독립 검증 / 인간 최종 판단" 3구조 (그대로 새 3축)
- 점수 0-100 → 4단계 상태 + 근거 수
- 카드 수 강제 → 레버리지 기준 동적 0-3 (기본값 1)
- "이 도구가 못 본 것" 상시 노출
- ai_prompt 6 라벨 중 두 개 갱신 (`[지금 상황]` → `[이번 변경의 이유]`, `[끝나고 확인]` → `[성공 기준과 직접 확인 방법]`)

이번 변경은 위 권고를 코드·스펙까지 끌어내린다. 슬로건("주인이 있는 프로젝트")은 사용자 노출용으로 유지.

## Goals / Non-Goals

**Goals:**
- 3축을 `intent / verification / continuity` (의도 / 검증 / 이어받기) 로 재설계하고 측정 신호를 8 운영 정의에서 매핑한다.
- 점수 표시를 4단계 상태(`strong / moderate / weak / unknown`) + 근거 수 + 대표 근거로 바꾼다. 0-100 원시 점수는 payload에 노출하지 않는다.
- 다음 행동 카드 수를 약점 수 강제 매핑 → 레버리지 기준 동적 0-3개로 바꾼다 (기본값 1개).
- 액션 0개일 때 침묵·칭찬·판단 보류를 분리해서 표시한다.
- "이 도구가 못 본 것" 블록을 Briefing 영역 하단에 고정 표시한다.
- ai_prompt 6 라벨 중 두 개를 권고대로 갱신하고 PROMPT_VERSION을 bump한다.
- 약한 process proxy(feat/fix 비율, spec 커밋 시점 등)를 단독 판정 근거에서 제외한다.

**Non-Goals:**
- 새 신호 수집기 추가 (예: `.cursor/`, `.copilot/` 같은 새 도구 흔적). 이번에는 현재 수집 가능한 신호만 재분류·재해석.
- 점수 산정 알고리즘의 머신러닝화 — 결정론 유지.
- AI 어댑터 자체 변경(codex/claude CLI). 프롬프트 텍스트만 갱신.
- 시니어 사용자용 별도 화면. 페르소나 분리는 직전 변경에서 끝.
- payload schema 의 외부 호환성 보장 — 자기 적용 + CivilSim 외에 소비자 없음, BREAKING 허용.

## Decisions

### Decision 1: 새 3축 정의와 측정 신호 매핑

**중요**: 신호 리스트는 *공통 분모*로 작성한다 (특정 도구·프로젝트의 컨벤션을 표준처럼 박지 않음). ROBOCO/OMC/OpenSpec 컨벤션은 *옵션 중 하나*로만 등장한다. 그래야 OpenSpec 안 쓰는 일반 오픈소스 레포도 공정하게 평가된다.

#### intent (의도) 축

"이 프로젝트의 의도가 외부 AI 세션에 전달 가능한가". 3 sub-category 의 충족도로 측정:

**(a) AI 지속 지시 문서가 1종 이상 존재 + 충실도 임계 충족**
- 인정 후보 (어느 것이든 1 신호): `CLAUDE.md` (Anthropic), `AGENTS.md` (OpenAI Codex), `.cursorrules` 또는 `.cursor/rules/*` (Cursor), `.github/copilot-instructions.md` (Copilot), `.windsurf/*` (Windsurf), `.aider.conf.yml` (Aider), `.continue/*` (Continue) 등
- 충실도 임계: 파일 크기 ≥ 500 chars + 항목 헤더 ≥ 2 (단순 빈 파일 방지)

**(b) 프로젝트 의도 문서가 1종 이상 존재**
- 인정 후보 (어느 것이든 1 신호): README 의 *purpose 문단* (단순 설치 지시가 아닌 "what / why" 설명), `docs/intent.md`, `VISION.md`, `ABOUT.md`, `PROJECT.md`, `OVERVIEW.md`, `openspec/project.md`
- README purpose 감지 휴리스틱: README 첫 1-3 단락 안에 "what", "purpose", "why", "이 프로젝트는", "이 도구는" 같은 키워드 포함 + 단락 길이 ≥ 200 chars

**(c) 의도와 비의도가 먼저 적혀 있는 흔적**
- 인정 후보: 의도 문서의 `Not` / `Out of Scope` / `Non-Goals` 섹션, `docs/adr/` 또는 `docs/decisions/` (ADR), CHANGELOG.md 가 *reasoning* 포함 (단순 변경 목록 아님), openspec proposal Why

#### verification (검증) 축

"결과를 인간이 독립적으로 확인할 수 있는가". 3 sub-category:

**(a) 손 검증 흔적**
- 인정 후보: `docs/validation/` (또는 비슷한 검증 디렉토리), `screenshots/` 또는 `screenshot/`, `demo/` 또는 `docs/demo/`, 수동 테스트 체크리스트 문서

**(b) 자동 테스트와 CI**
- 자동 테스트 풀: `tests/`, `__tests__/`, `*_test.py`, `*.test.ts`/`*.test.js`, `spec/` (Ruby), `t/` (Perl) 등 언어별 표준 위치
- CI 풀: `.github/workflows/`, `.gitlab-ci.yml`, `.circleci/`, `azure-pipelines.yml`, `Jenkinsfile`

**(c) 재현 가능 실행 경로**
- 인정 후보: README 의 명령어 블록 (\`\`\` 안 build/test/run), `package.json` scripts 필드, `pyproject.toml` 의 `[project.scripts]` 또는 `[tool.poetry.scripts]`, `Makefile`, `justfile`, `Dockerfile`, `docker-compose.yml`, `.env.sample`/`.env.example`

#### continuity (이어받기) 축

"다음 세션이 이어받을 수 있는가". 3 sub-category:

**(a) 작게 이어가기**
- 인정 후보: 작은 PR/commit 빈도 (git history 분석 — 평균 commit 크기 임계 이하), saved plans (`openspec/changes/*/tasks.md`, `PLANS.md`, `TODO.md`, `ROADMAP.md`), GitHub issue 템플릿 (`.github/ISSUE_TEMPLATE`)

**(b) 학습 반영**
- 인정 후보: 회고 디렉토리 (`docs/retro/`, `docs/postmortem/`, `docs/lessons/`), CHANGELOG.md 갱신 빈도 ≥ 임계, `AGENTS.md`/`CLAUDE.md` 주기적 업데이트 (git log — 최근 N개 커밋에 갱신 흔적)

**(c) 핸드오프**
- 인정 후보: `HANDOFF.md`, `ONBOARDING.md`, `CONTRIBUTING.md`

#### 우리가 못 보는 것 (blind spot 추가)

- Notion / Confluence / 사내 위키 — 코드 외부에 의도가 있을 수 있음
- Slack / Linear / Jira — 외부 도구의 결정 로그
- README purpose 문단 — 키워드 매칭만으로 *진짜로 의도가 담겨있는지* 못 판단

이 셋은 사각지대 블록에 한 줄 추가:
> "외부 도구(Notion, Slack, Linear 등)와 README 의 *질적 깊이* 는 자동 판단 못 합니다."

대안: 4축(detect/intent/verify/continuity) — detect를 별도 축으로. 반려: 감지는 *전제*이지 평가 차원이 아님. 현재 처럼 전제 게이트로 둠.

### Decision 2: 8 운영 정의 중 6개만 점수에 반영, 2개는 사각지대로 분리

채택:
- 점수 산정에 들어가는 것 (흔적 측정 가능): 의도 글, 의도+비의도 먼저, 손 검증, 재현 가능 실행 경로, 학습 반영, 작게 이어가기 — 6개
- 점수 산정에 *들어가지 않는* 것 (대화·관찰 필요): 설명할 수 있다, 다음 행동을 사람이 정한다 — 2개

후자는 payload의 `blind_spots` 필드로 분리되어 UI에 *항상 명시적으로 노출*된다 (Playwright/Section 508 패턴).

대안: 8개 모두 점수에 반영 — 측정 못 하는 차원을 점수에 섞으면 흔적 기반 가짜 정확성 위험. 반려.

### Decision 3: 점수 표시 0-100 → 4단계 상태

채택: 각 축은 다음 4상태 중 하나로 표시한다.
- `strong` — 신호 수가 *충분히 많고 다양*하다 (axis 별 임계 정의)
- `moderate` — 신호가 일부 있지만 핵심 신호 일부 결손
- `weak` — 핵심 신호가 결손
- `unknown` — 신호 수집 자체가 실패 또는 의미 있는 판단을 위한 데이터 부족 (예: git history 없음, 너무 이른 시점)

각 상태에 함께 노출되는 것: `signal_count`(인지된 신호 개수), `top_signals`(대표 근거 2-3개, 파일 경로/문서 라벨).

내부 보존: 0-100 원시 점수는 `_raw_score` (또는 동등 비공개 필드) 에 디버그용으로 보존하되 SPA 화면에 *기본 노출하지 않음*. 토글로만 접근(개발자 영역).

대안 1: 점수 완전 제거 — 디버그성·회귀 추적이 어려움. 반려.
대안 2: 4단계 + 점수 동시 표시 — 사용자 인지 부하·점수 의존 회귀 위험. 반려.

임계값 (비율 기반 — 신호 풀 크기가 축마다 다르므로 절대치 아닌 비율):
- `strong`: 인지 신호 ≥ **70%** + 핵심 신호 모두 충족
- `moderate`: 인지 신호 ≥ **40%**
- `weak`: 인지 신호 ≥ **10%**
- `unknown`: 데이터 수집 실패 또는 모든 신호 0%

핵심 신호 (strong 의 필수 조건 — 비율 70% 만으로 부족, 다음도 같이 충족):
- `intent`: AI 지속 지시 문서 1종 이상 + 프로젝트 의도 문서 1종 이상
- `verification`: 자동 테스트 + 재현 가능 실행 경로 둘 다
- `continuity`: 작은 PR 패턴 + saved plans 1종 이상

자기 적용 데이터 보고 임계값 조정 가능. 특히 70% 가 너무 까다로우면 60% 로 완화 검토.

### Decision 4: 카드 수 동적 0-3개, 기본값 1개, 레버리지 기준 (9 룰)

채택: 약점을 단순 카운트로 카드화하지 않고 *루트 원인별 9 룰* 로 그룹화 후 영향이 큰 순으로 카드 생성.

**9 룰** (코드에 박음 — 결정론):

| # | 결손 정의 (한 풀 안에서 모두 부재) | 합성 카드 작업 |
|---|---|---|
| 1 | AI 지속 지시 문서 (CLAUDE.md / AGENTS.md / .cursorrules / .windsurf / .aider / .continue / copilot-instructions) | "AI 지침 문서 셋업 (이 중 하나)" |
| 2 | 프로젝트 의도 문서 (README purpose / VISION / ABOUT / PROJECT / OVERVIEW / intent.md / project.md) | "프로젝트 의도 문서화" |
| 3 | 의도+비의도 명문화 (Not 섹션 / ADR / decisions/ / CHANGELOG reasoning / proposal Why) | "비의도·근거 명문화" |
| 4 | 자동 테스트 (tests/ / __tests__/ / *_test.* / spec/) | "자동 테스트 도입" |
| 5 | CI (.github/workflows / .gitlab-ci / .circleci / Jenkinsfile) | "CI 설정 추가" |
| 6 | 재현 가능 실행 경로 (README cmd / package.json scripts / pyproject scripts / Makefile / Dockerfile) | "실행 경로 셋업" |
| 7 | 손 검증 흔적 (validation/ / screenshots / demo / 체크리스트) | "수동 검증 흔적 도입" |
| 8 | 학습 반영 (회고 / postmortem / lessons / CHANGELOG / 지시 문서 갱신) | "회고-학습 사이클 도입" |
| 9 | 핸드오프 (HANDOFF / ONBOARDING / CONTRIBUTING) | "핸드오프 문서 추가" |

**매칭 알고리즘**:
1. 결손 신호 셋 수집 (각 sub-category 의 *모든 후보 부재* 케이스)
2. 9 룰과 매칭 — 결손 정의의 풀과 *교집합 ≥ 1* 이면 그 룰 작업이 후보
3. 후보 작업들을 *해결되는 결손 신호 수* 내림차순 정렬
4. 최종 카드 수 결정:
   - 가장 큰 root 1 개 + 그 카드가 두 개 이상의 결손 동시 해결 → **카드 1개** (기본)
   - 서로 독립적인 고확신 root 2 개 → **카드 2개**
   - 서로 겹치지 않는 고확신·저중복 root 3 개 → **카드 3개** (최대)
   - 고확신 root 0 개 → **카드 0개** (zero-action 분기 적용)

**Sub-category fallback**: 9 룰 중 어느 것에도 매칭 안 된 결손이 남으면 sub-category 단위로 일반 카드 1 개 생성 (예: "intent 영역 보완 필요"). 자기 적용·CivilSim 검증에서 fallback 빈도 측정 후 새 룰 추가.

대안: 약점 N → 카드 min(N, 3) 단순 매핑 — 직전 구현. 반려 (가짜 노이즈, alert fatigue).
대안: AI 호출로 결손 묶기 — 변동성·비용↑, 결정론 우선 원칙 깨짐. 반려 (미래 변경에서 재검토).

### Decision 5: 침묵 / 칭찬 / 판단 보류 분리 + 강한 긍정 신호 정의

채택: 카드 0개 상태에서 다음 셋을 분기.

**"강한 긍정 신호" 정의** = 어느 축이 `strong` 상태인 것. (그 축의 신호가 70% 이상 충족 + 핵심 신호 모두 OK)

**분기**:
- **칭찬** — 카드 0개 + 강한 긍정 신호 ≥ 1 (어느 축 strong)
  - 형식: "{축 한국어 이름} 축이 강함 — {top_signals 1-2 개 인용}. 이 습관을 유지하세요."
  - 두 축 strong → 두 축 모두 인용
  - 세 축 모두 strong → "전반적으로 잘 갖춰져 있음. 다음 변경에 자신감 가지세요." + 각 축 한 줄
- **판단 보류** — 카드 0개 + 강한 긍정 신호 0 + 사각지대만 남음
  - 형식: "코드만 봐선 추가 진단 어려움 — 사용자 대화·시연이 필요합니다"
  - 칭찬 안 함 (거짓 칭찬 위험 차단)
- **침묵** — 카드 0개 + 위 둘 모두 해당 없음
  - 메시지 없음 (드문 케이스, 빈도 측정)

대안: 0개일 때 무조건 칭찬 — "잘하고 있다" 가 거짓일 수 있음. 반려.
대안: 최근 추가된 신호 인용 — process proxy 와 같은 종류, 약점 있음. 반려.

### Decision 10: 평가 철학 토글 — 사용자에게 "어떻게 평가하는지" 투명하게 노출

채택: Briefing 화면 하단에 *접힘/펼침 토글* 형태로 "이 도구가 바이브코딩을 어떻게 평가하나요?" 섹션을 둔다. 펼치면 슬로건 → 운영 정의 → 8 신호 → 3축 매핑 → 4 단계 상태 의미 → 카드 수 정책 → 사각지대 → 출처 순으로 노출.

**왜**:
- 사용자가 결과 라벨 (예: "intent 약함") 을 봤을 때, *왜 그렇게 판정됐는지* 따라가는 길이 있어야 한다.
- "주인이 있는 프로젝트" 슬로건이 어떻게 8 신호로 풀어지는지 보여주는 게 *우리 도구의 정직성* 의 일부.
- 리서치 출처 (Anthropic / OpenAI / Karpathy / Simon Willison / Kent Beck / Spec Kit / BDD 등) 를 인용해 신뢰 형성.

**위치**: vibe coding 섹션 *최하단* (blind spot 블록 아래) 또는 Briefing 화면 *footer 영역*. 기본 *접힌 상태* (사용자 부담 최소화).

**구조** (8 sub-section):
1. 슬로건 한 줄 — "주인이 있는 프로젝트"
2. 운영 정의 3 구조 — 외부화된 의도 / 독립 검증 / 인간 최종 판단
3. 8 운영 신호 — 흔적 6 + 사각지대 2
4. 3축 매핑 — 어느 신호가 어느 축에 매핑되는지
5. 4 단계 상태 의미 — strong / moderate / weak / unknown 각각의 뜻과 임계
6. 카드 수 정책 — 왜 0-3 동적인가
7. 사각지대 4 항목 재명시 — "이 도구가 못 보는 것"
8. 출처 — 리서치에서 인용한 핵심 자료

토글 콘텐츠 *텍스트* 자체는 사용자와 별도 검토. 본 design.md 는 *구조*만 정의.

**대안**: 별도 페이지 (`/about` 또는 `/methodology`) — 클릭 1회 더, 사용자가 안 누름. 반려. 토글이 더 노출됨.

**근거**: 자동 접근성 도구·정적분석 도구의 좋은 사례 (Playwright, Section 508, SonarQube) 가 모두 *방법론을 명시*. 신뢰는 알고리즘 정확성보다 *방법론 투명성*에서 더 자란다.

### Decision 6: blind spot 상시 노출

채택: Briefing 영역 *모든 화면*에 다음 블록을 고정 노출.

```
이 도구가 못 본 것:
- 사용자(나)가 What/Why/Next 를 자기 입으로 설명할 수 있는가
- 손으로 한 검증이 *실제로 매번* 굴러가는가
- 다음 행동의 우선순위를 사람이 정하고 있는가
이 셋은 코드만 봐서는 판단 못 합니다. 화면 점수와 무관하게 자가 점검해 주세요.
```

위치: 검토 경고 배너 *바로 아래* 또는 vibe coding 섹션 하단. UI 결정은 구현 단계.

### Decision 7: ai_prompt 6 라벨 두 개 갱신

채택:
- `[지금 상황]` → `[이번 변경의 이유]` (상태 서술 → 동기 강조)
- `[끝나고 확인]` → `[성공 기준과 직접 확인 방법]` (검증 순서 → 완료 기준 + 확인 방법)
- 나머지 4 라벨 불변: `[현재 프로젝트]`, `[해줄 일]`, `[작업 전 읽을 것]`, `[건드리지 말 것]`

필수 라벨 셋(parser 폴백 트리거): `[현재 프로젝트]`, `[해줄 일]`, `[성공 기준과 직접 확인 방법]`. 직전 변경의 `[끝나고 확인]` 검사를 새 라벨로 교체.

PROMPT_VERSION: v6-persona-split → **v7-realign**.

### Decision 8: 약한 process proxy 강등

채택: feat/fix 비율, spec 커밋 시점 순서, hotspot 누적 속도, intent 문서 업데이트 빈도 — 모두 단독 판정 근거에서 제외하고 *보조 정보 패널* 로만 노출. payload 에는 `process_proxies` 같은 별도 필드로 분리.

근거: Goodhart 위험. squash merge 같은 운영 차이로 왜곡. 직접 신호(rationale, validation artifact, plan)가 같은 측면을 더 강하게 본다.

### Decision 9: 슬로건 vs 운영 정의 두 층 구조

채택:
- 사용자 노출 슬로건: **"주인이 있는 프로젝트"** (`docs/intent.md` Why)
- 스펙·코드 운영 정의: **"외부화된 의도 / 독립 검증 / 인간 최종 판단"** + 8 신호 (`vibe-coding-insights/spec.md`)

브리핑 화면 어딘가에 슬로건도 한 번 노출(예: vibe coding 섹션 헤더). 슬로건 클릭/hover시 운영 정의 펼침은 구현 단계.

## Risks / Trade-offs

- **[리스크] 4단계 상태 임계값을 적절히 못 잡으면 모든 레포가 `weak` 또는 `moderate` 로 몰릴 수 있다** → mitigation: 자기 적용 + CivilSim 두 케이스 검증 후 임계 조정. 본 변경 archive 전에 "CodeXray 자체는 `strong`/`moderate`/`weak` 중 무엇으로 분류돼야 하는가" 사용자 합의를 받음.
- **[리스크] axes.py 큰 변경으로 회귀** → mitigation: 결정론적 직렬화 byte-identical 테스트 유지, 기존 시나리오 테스트는 새 축으로 갱신, 새 시나리오 테스트 신규.
- **[리스크] PROMPT_VERSION + SCHEMA_VERSION 동시 bump → 캐시 더블 무효화** → mitigation: 1회 비용. 모든 자기 적용이 한 번 AI 재호출. 비개인 머신 영향 없음.
- **[리스크] "이 도구가 못 본 것" 블록이 사용자에게 *우리 도구가 못 미덥다* 인상** → mitigation: 표현을 *겸손한 한계 명시* 가 아니라 *자가 점검 체크리스트* 로 프레이밍. 톤은 신뢰 무너뜨리는 게 아니라 자기책임 강화.
- **[리스크] 카드 수 동적 0-3 정책으로 0개 상황이 자주 나오면 사용자가 "도구가 안 일한다" 인식** → mitigation: 0개 + 칭찬 메시지가 정상 패턴. 자기 적용에서 빈도 측정 후 0개 너무 많으면 임계 재조정. 단, 임계 재조정의 동기가 *사용자 만족* 이 아닌 *현실 정확성* 임을 design에 박음.
- **[트레이드오프] 두 변경 1주 안 연속으로 ai_prompt 라벨 갱신** → 캐시 한 번 더 무효화. 비개인 사용자 없으니 수용 가능. archive note에 명시.
- **[트레이드오프] 슬로건 vs 운영 정의 두 층 = 약간의 인지 비용** → 슬로건은 1순위 청자(비개발자)에 직관적, 운영 정의는 스펙/코드 기준. 두 층 분리가 모순 아니라 *역할 분리*.

## Migration Plan

1. PROMPT_VERSION + SCHEMA_VERSION 동시 bump → 캐시 자동 무효화. 별도 cache clear 불필요.
2. payload schema 변경 (axis name 변경, score → state) → 자기 적용 외 외부 소비자 없음. SCHEMA_VERSION 5 → 6.
3. 롤백: PROMPT_VERSION/SCHEMA_VERSION revert + axes.py / briefing_payload.py / 프론트 컴포넌트 revert. 직전 archive 시점 코드는 git tag 또는 commit hash로 복구 가능.
4. 단계적 적용 안 함 — 한 번에 commit하고 자기 적용 검증으로 안정성 확인.

## Open Questions

- **임계값 정확치**: `strong / moderate / weak` 의 신호 개수 임계는 4 / 2 / 1 이 초안. 자기 적용 데이터 보고 조정 필요.
- **사각지대 블록 위치**: vibe coding 섹션 하단 vs 검토 배너 바로 아래 vs 화면 최하단 — 구현 단계에서 가독성 보고 결정.
- **슬로건 노출 위치**: vibe coding 섹션 헤더 vs intent_alignment 옆 vs Briefing 최상단 — 구현 단계 결정.

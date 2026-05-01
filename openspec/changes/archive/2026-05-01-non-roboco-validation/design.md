## Context

직전 archive `vibe-insights-realign` 으로 vibe coding 평가가 3 축 + 4 단계 상태 + 9 룰 카드 합성으로 재설계됐다. 그러나 검증 데이터는 **CodeXray 자기 적용 1 회** 뿐이고 그 결과는 모든 축이 `moderate` 로 몰렸다. 다음의 두 가지를 입증할 데이터가 없다:

1. **편향**: 신호 풀 정의가 ROBOCO/OMC 컨벤션 (`.claude/`, `.omc/`, `openspec/`, `docs/validation/` 한국어 회고) 에 무의식적으로 맞춰졌는가? 일반 OSS 가 쓰는 동등한 도구·관행을 놓치고 있는가?
2. **임계값**: `strong ≥ 70%`, `moderate ≥ 40%`, `weak ≥ 10%` 가 적정한가? 분포가 한쪽으로 몰리지 않는가?

본 변경은 외부 OSS 5–7 개로 데이터를 모아 위 두 질문에 답하기 위한 권고안을 만든다. 권고를 *실제 코드로 반영하는* 변경은 별도(`vibe-thresholds-tune` 또는 `vibe-signal-pool-expand` 등) 로 분리한다.

이해관계자: 사용자(프로젝트 오너) — 데이터 기반 의사결정을 원함. 자기 1 회 데이터에 의존한 임계값 조정에 명시적으로 반대 의사를 표명함 ("자기 적용 1 회만으로는 데이터 부족").

## Goals / Non-Goals

**Goals:**
- 외부 OSS 5–7 개에 대한 vibe_insights 결정론 분석 결과를 표·통계로 정리한다.
- 3 축 상태 분포·신호 풀 ratio 분포·blind spot 응답 패턴을 한 문서에 모은다.
- 데이터 기반 권고안 (임계값을 그대로 둘지·낮출지·올릴지, 신호 풀에 무엇을 추가할지) 을 작성한다.
- 다음 임계값/풀 조정 변경이 *언제든 동일 방법으로 재검증* 될 수 있도록 절차를 spec 화한다.

**Non-Goals:**
- 임계값 또는 신호 풀의 *실제 코드 수정* (단, 명백한 false positive 1–2 건 즉시 수정은 허용).
- AI 호출 결과 평가 (편향·비용·재현성 문제로 차단).
- 외부 레포 자동 clone (사용자가 사전에 로컬에 준비 — 본 도구의 `로컬만` 원칙 유지).
- 통계적 유의성 증명 (n=5–7 은 분포 *경향* 확인용; 가설 검정 아님).

## Decisions

### 결정 1: 검증 대상 레포 선정 — 의도된 다양성 7 개

| 레포 | 성격 | 기대 신호 패턴 |
|---|---|---|
| `vitejs/vite` | JS 빌드 도구, 거대 OSS | AI 지시 문서 없음 / 강한 자동 검증 / 작은 PR 문화 |
| `tiangolo/fastapi` | Python 프레임워크, 한 명 주도 | 강한 의도 문서 (README 깊은 purpose) / 강한 검증 / 회고 약함 |
| `astral-sh/ruff` | Rust 린터, 신생 OSS | CHANGELOG 강함 / spec 약함 / 매우 작은 PR |
| `sqlite/sqlite` | C 전통 OSS | AI 지시 0 / 검증 강함 (자체 테스트) / 의도 문서 다른 형식 |
| `anthropics/anthropic-cookbook` | AI-first 예제 레포 | CLAUDE.md 가능성 / 검증 약함 / 의도 명시적 |
| `nrwl/nx` | 모노레포 도구 | `.cursor/` 또는 `.windsurf/` 가능성 / docs 강함 |
| 사용자가 직접 보유한 1 개 (예: CivilSim) | 단일 사용자 dogfood | 비교 기준점 — 자기 적용과 다른 페르소나 결과 확인 |

**대안**: GitHub trending top 50 무작위 — 기각. 다양성이 의도되지 않으면 분포가 의미 없음.

**대안**: 100 개 이상 대규모 — 기각. clone/분석 시간 비현실적, 본 변경 범위 초과.

### 결정 2: 일괄 분석 스크립트는 `scripts/validate_external_repos.py`

CLI 서브커맨드(`codexray validate-external`) 와 비교:

- 스크립트: 검증 절차가 dev 도구임을 명시. 사용자에게 노출되는 CLI 표면적이 늘지 않음. 임시 코드 성격.
- 서브커맨드: 영구 기능처럼 보임. 사용자 혼란 위험.

→ **스크립트 채택.** 향후 정기 재검증이 필요하면 그때 CLI 로 승격 검토.

스크립트 입력: 레포 경로 리스트 (텍스트 파일 또는 인자). 출력: `docs/validation/non-roboco-data/{repo}.json` (vibe_insights payload 그대로) + 콘솔 요약.

### 결정 3: AI 호출 차단

`build_briefing_payload` 의 결정론 부분 (`build_vibe_insights` + 3 축 신호 수집 + blind spot + process proxies) 만 호출. AI narrative / 카드 합성 AI 호출 모두 스킵.

이유:
- AI 출력은 비결정적 — 동일 입력에서 분포 비교가 불가능.
- AI 호출 비용 (7 개 × 카드 합성 = 의미 있는 비용).
- 본 변경 목적은 *결정론 신호의 적정성 검증*. AI 출력은 신호 위에서 동작하므로 신호가 정리되면 자동으로 개선됨.

### 결정 4: 결과 문서 형식

`docs/validation/non-roboco-validation-results.md` 한 파일에:

1. **요약 표**: 레포 × 3 축 상태 매트릭스 (한 화면에 분포 보임)
2. **신호 풀 ratio 분포**: 각 축별 ratio 의 7 레포 분포 (히스토그램 또는 텍스트 분포)
3. **누락된 신호 사례**: 사람이 보면 명백히 vibe coding 잘 한 것 같은데 도구가 weak 으로 분류한 사례 → 어떤 신호를 놓쳤는지
4. **과탐지 사례**: 도구가 strong 으로 분류했지만 실제로는 빈약한 사례
5. **권고안**: 임계값 (그대로/조정/형식 변경), 신호 풀 추가 후보, blind spot 추가 후보
6. **후속 변경 제안**: `vibe-thresholds-tune` 등 별도 변경 후보 명세

### 결정 5: 명백한 false positive 즉시 수정의 경계선

본 변경에서 코드를 *건드릴 수 있는 조건* 은 다음 모두 만족:
- 사람이 봐도 명백한 오류 (예: README 1 줄짜리에 "purpose" 단어가 있어 휴리스틱 통과)
- 수정이 1 함수 1 줄 수준
- 기존 테스트가 통과해 회귀 없음

조건을 *하나라도* 어기면 후속 변경으로 넘긴다. 이 정책을 spec 시나리오에 명시한다.

## Risks / Trade-offs

- [n=7 의 통계적 한계] → "분포 경향 관찰" 로 명시하고 가설 검정처럼 다루지 않음. 향후 n 확장은 별도 변경.
- [외부 레포 clone 부담] → 스크립트가 clone 하지 않고 *이미 로컬에 있는 경로* 만 받음. 사용자가 `~/repos/` 등에 준비.
- [false positive 즉시 수정의 회귀 위험] → 결정 5 의 3 조건 + 기존 309 테스트 + 자기 적용 재실행으로 회귀 차단.
- [선정 레포의 편향] → 결정 1 의 다양성 매트릭스를 spec 시나리오로 명문화해 다음 검증 시 재현 가능하게 함.
- [AI 출력 미평가] → 결정 3 에서 명시. 후속 변경에서 AI narrative 품질 검증을 별도 진행.

## Migration Plan

본 변경은 *측정 + 문서화* 변경이라 마이그레이션이 거의 없음:

1. 스크립트 추가 → 단위 테스트 1–2 개로 회귀 차단.
2. 검증 결과 문서 작성 → 사용자가 직접 검토.
3. 명백한 false positive 수정 (있으면) → 기존 테스트 통과 + 자기 적용 재실행으로 검증.
4. SCHEMA_VERSION/PROMPT_VERSION bump 없음 (캐시 영향 없음).
5. archive 후 후속 변경 제안 (`vibe-thresholds-tune` 등) 을 CLAUDE.md 에 기록.

롤백: 스크립트 + 문서 삭제 + (있다면) false positive 수정 revert. 단순.

## Open Questions

- 사용자가 7 개 레포를 모두 로컬에 보유하지 않은 경우 → 보유한 것만으로 진행할지 여부. 기본값: **보유한 것만으로 진행, 누락 사실을 결과 문서에 명시.**
- `anthropics/anthropic-cookbook` 처럼 "AI-first 인데 비-vibe 코딩" 인 레포의 분류 — 시작 가이드로 떨어질지 / 약한 strong 으로 잡힐지 → 데이터로 답변.

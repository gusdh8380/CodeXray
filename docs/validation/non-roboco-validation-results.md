# non-roboco-validation — 결과 문서

**날짜**: 2026-05-02
**대상**: 외부 OSS + 사용자 보유 레포 9 개
**목적**: 직전 archive `vibe-insights-realign` 으로 도입된 3 축 + 4 단계 상태 + 신호 풀의 ROBOCO 편향과 임계값 적정성을 외부 데이터로 검증

데이터 raw: `docs/validation/non-roboco-data/*.json` (9 개 결정론 페이로드, AI 호출 차단)

---

## 1. 레포 × 3 축 상태 매트릭스

| 레포 | 출처 | 언어 | 의도 | 검증 | 이어받기 |
|---|---|---|---|---|---|
| **CodeXray** (자기) | ROBOCO | Python | strong 3/3 (100%) | strong 3/3 (100%) | strong 3/3 (100%) |
| **fastapi** | 외부 OSS | Python | **NOT DETECTED** | — | — |
| **OpenSpec** | 외부 (Fission-AI) | TS | weak 1/3 (33%) | moderate 2/3 (67%) | moderate 2/3 (67%) |
| **openclaw** | 외부 (fork) | TS | strong 3/3 (100%) | moderate 2/3 (67%) | strong 3/3 (100%) |
| **graphify** | 외부 (claude skill) | Python | moderate 2/3 (67%) | moderate 2/3 (67%) | moderate 2/3 (67%) |
| **roboco-cli** | ROBOCO | TS | weak 1/3 (33%) | moderate 2/3 (67%) | strong 3/3 (100%) |
| **CivilSim** | 사용자 dogfood | C# | weak 1/3 (33%) | weak 1/3 (33%) | weak 1/3 (33%) |
| **StructFlow** | 사용자 | C# | weak 1/3 (33%) | moderate 2/3 (67%) | moderate 2/3 (67%) |
| **water-treatment-rag** | 사용자 | Python | moderate 2/3 (67%) | weak 1/3 (33%) | moderate 2/3 (67%) |

**다양성 매트릭스 점검** (design.md 결정 1):
- 언어: Python / TS / C# 충족 (Rust / C / Go 부재 — 향후 확장 권고)
- 연령: 신생 위주 — 성숙 (≥ 5 년) OSS 부재. fastapi(2018-) 가 유일한 성숙 후보였으나 detection 게이트에서 탈락
- AI 도입 단계: AI-first 7 / 비-AI 1 (fastapi) / fork 후 AI 도입 1 (openclaw) — 비-AI 케이스가 사실상 1 개로 부족

---

## 2. 축별 신호 풀 ratio 분포

감지된 8 개 (fastapi 제외) 중:

| 축 | strong | moderate | weak | unknown |
|---|---|---|---|---|
| 의도 | 2 (CodeXray, openclaw) | 2 (graphify, water-treatment-rag) | 4 (OpenSpec, roboco-cli, CivilSim, StructFlow) | 0 |
| 검증 | 1 (CodeXray) | 5 | 2 (CivilSim, water-treatment-rag) | 0 |
| 이어받기 | 3 (CodeXray, openclaw, roboco-cli) | 4 | 1 (CivilSim) | 0 |

**분포 해석**:
- 의도 축은 **weak 으로 치우침** — 4/8 이 weak. "AI 지속 지시 문서 + 프로젝트 의도 문서 + 의도/비의도 명문화" 셋을 모두 갖춘 레포가 적음. 강한 ROBOCO 시그니처(`docs/intent.md` + `openspec/`).
- 검증 축은 **moderate 중심** — 5/8. "손 검증 흔적(`docs/validation/`)" 1 개 신호가 거의 모든 레포에서 빠짐. 이 신호가 ROBOCO 컨벤션에 강하게 묶여 있음.
- 이어받기 축은 **위쪽으로 치우침** — 작게 이어가기 (git history) 가 거의 항상 통과. CHANGELOG.md 가 흔함. 핸드오프 문서가 결정 신호.

**임계값 70/40/10 자체는 분포가 3 단계에 잘 퍼지므로 큰 결함 없음.** 그러나 신호 풀 자체가 ROBOCO 컨벤션에 편향됨 — 같은 데이터로 임계값을 조정하면 결국 같은 편향을 다른 비율로 표현할 뿐.

---

## 3. 누락된 신호 사례 (false negative)

### 3.1 fastapi NOT DETECTED — 가장 큰 결함

**근거**: `src/codexray/vibe_insights/detection.py:8` 의 `_STRONG_PATHS = ("CLAUDE.md", "AGENTS.md", ".claude", ".omc", "openspec")` 게이트.

fastapi 는 vibe coding 의 8 개 운영 신호 중 *흔적 기반 6 개* 가운데 다음을 명백히 갖춤:
- 손 검증 흔적: `tests/` + 거대한 `docs/`
- 자동 테스트와 CI: `.github/workflows/test.yml`
- 재현 가능 실행 경로: `pyproject.toml` scripts + `scripts/` 디렉토리
- 재현 가능 실행 경로: README 명령 블록 다수
- 학습 반영: `CHANGELOG.md` + 거대 commit history
- 작게 이어가기: ~1 만 commits

그러나 `_STRONG_PATHS` 가 모두 부재이고 vibe analyzer 의 `confidence` 도 high 가 아니라 *detection 자체에서 떨어짐* → 시작 가이드만 받음.

**해석**: detection 은 "AI 협업 흔적" 을 찾는 게이트이고 vibe coding 평가는 "AI 협업 환경에서의 책임감" 을 평가. 두 개가 맞물리면 — *AI 도구를 도입한 레포만 평가 가능*. 이게 설계 의도인지 결함인지 사용자 결정 필요.

### 3.2 OpenSpec 의도 weak — AGENTS.md 0 byte

OpenSpec 도구 자체는 외부 AI-first 도구(AGENTS.md + `openspec/` 디렉토리 존재) 인데 의도 33%. 원인:
- `AGENTS.md` 가 0 byte (빈 파일) → `_MIN_GUIDE_SIZE = 500` 임계 미달
- `openspec/project.md` 가 없음 (도구 자체이지 적용 레포가 아님)

**도구 측 결함 아님** — 측정은 정확. 그러나 사용자에게는 "OpenSpec 자체가 weak" 으로 보여 의문 발생. blind spot 메시지에 *"이 레포가 도구 자체일 수 있음"* 추가 검토 후보.

### 3.3 CivilSim 모든 축 33%

사용자 dogfood Unity C# 게임. CLAUDE.md 만 존재하고 그 외 신호가 모두 부재. 그러나 사용자가 "이전보다 좋아졌다" 고 평가한 — 즉 *실제 작업 흐름은 vibe coding* 이지만 도구가 못 잡는 흔적이 많음. blind spot 으로 노출되는 *"외부 도구(Notion, Slack 등)에 있는 의도·결정 흔적"* 영역이 클 가능성.

---

## 4. 과탐지 사례 (false positive)

### 4.1 openclaw 의도 strong 100% — fork 통과 의심

`origin: github.com/openclaw/openclaw` 의 fork. `git log` 가 3 commit 만 보여주는데 `git rev-list --count HEAD` 는 34608 (packed-refs / reflog 영향). 이 거대 fork 에 사용자가 CLAUDE.md / AGENTS.md / docs/intent.md 류를 추가했고 — 도구는 그걸 "의도가 글로 박혀 있다" 로 해석.

**문제**: AI 도구 파일을 *추가만 해도* 의도 strong 으로 잡힘. 의도의 *깊이* 를 못 봄. 수천 line 짜리 코드베이스에 빈약한 CLAUDE.md 한 줄을 더해도 같은 strong.

이건 평가 철학 토글의 7 번 (이 도구가 못 보는 것) 으로 이미 명시된 한계 — 결과 문서에 사례로 추가될 뿐.

### 4.2 "작게 이어가기" 가 거의 항상 통과

`_check_small_continuity` 에서 `history.commit_count >= 5` 만 충족하면 통과. 즉 5 commit 이상인 모든 레포에서 자동 통과. 변별력 없음.

**즉시 수정 후보 (design 결정 5 의 3 조건 점검)**:
- 명백한 false positive ✅ (5 commits 만으로 "작게 이어가기" 라 보기 어려움)
- 1 함수 1–수 줄 ✅ (임계값 5 → 합리적 다른 값으로)
- 회귀 없음? — 자기 적용 결과가 strong 100% 인 상황에서 이 신호 하나가 떨어져도 strong 유지될 수 있는지 확인 필요

→ **본 변경에서 즉시 수정하지 않음.** 이유: 임계값 변경은 design 결정 5 의 "임계값 비율 변경" 항목에 해당해 후속 변경으로 분리해야 함. 결과 문서의 권고안에 명시.

---

## 5. 권고안

### 5.1 임계값 (70 / 40 / 10): **그대로 유지**
분포가 3 단계에 잘 퍼져 있어 임계값 비율 자체는 합리적. 단 *데이터 7 개 기준 잠정 결론* — n 확장 후 재검토.

### 5.2 신호 풀 추가 후보 (후속 변경 `vibe-signal-pool-expand`)

**의도 축 — 프로젝트 의도 문서**:
- `pyproject.toml` 의 `description` + `keywords` 강한 경우
- `package.json` 의 `description`
- README 의 `## What`, `## Why`, `## Purpose` 명시 섹션 (현재는 첫 5 단락 키워드 매칭만)

**검증 축 — 손 검증 흔적**:
- `examples/`, `demo/`, `samples/` 디렉토리 (코드 demo 도 손 검증의 한 형태)
- README 의 "Try it" / "Demo" 링크
- Storybook (`.storybook/`)

**이어받기 축 — 핸드오프 문서**:
- `MAINTAINERS.md`, `CODEOWNERS`
- `docs/contributing/`, `docs/getting-started/`

### 5.3 detection 게이트 재설계 (후속 변경 `vibe-detection-rebalance` 또는 큰 변경 `vibe-evaluation-philosophy-v2`)

**핵심 결정 사항**: vibe coding insights 가 평가하는 대상은 무엇인가?
- 옵션 A — *AI 협업 레포 한정*: 현 detection 유지. fastapi 같은 비-AI OSS 는 "전통 방식" 분류 + 시작 가이드. 명확하고 일관됨. 단 사용자가 "의도/검증/이어받기는 AI 와 무관한 보편 원칙" 이라고 본다면 유효 범위가 좁아짐.
- 옵션 B — *모든 레포*: detection 게이트 제거 또는 약화. fastapi 가 strong 으로 잡힘 → 평가 대상 확장. 단 starter_guide 의 의미 (전통 → vibe 전환 가이드) 가 사라짐.
- 옵션 C — *이중 모드*: detection 결과에 따라 두 가지 라벨 노출. "AI 협업 진단" (현재) vs "프로젝트 책임감 진단" (보편). 각 라벨의 신호 풀이 다름.

→ **사용자 결정 필요**. 결정 없이 변경 진입하지 말 것.

### 5.4 blind spot 추가 후보 (즉시 수정 가능 — design 결정 5 충족)

현재 4 항목 외에 다음 추가 검토:
- *"이 레포가 도구 자체이거나 fork 일 수 있습니다 — 그 경우 결과 해석에 주의"*
- *"AI 지시 문서가 *추가만* 됐을 뿐 깊이가 없을 수 있습니다"*

→ blind spot 은 코드에서 단순 문자열 추가라 design 결정 5 의 3 조건 (명백 / 1 함수 / 회귀 없음) 충족. 그러나 후속 변경에서 사용자와 합의 후 추가가 더 안전. **본 변경에서는 추가하지 않음**.

---

## 6. 후속 변경 제안

| 후보 | 우선순위 | 이유 | 본 결과 문서의 근거 섹션 |
|---|---|---|---|
| `vibe-detection-rebalance` (또는 `vibe-evaluation-philosophy-v2`) | **1순위** | fastapi NOT DETECTED 는 본 도구의 가장 큰 사용성 결함. 옵션 A/B/C 결정 후 진입 | §3.1, §5.3 |
| `vibe-signal-pool-expand` | 2순위 | 신호 풀이 ROBOCO 컨벤션에 편향됨을 직접 해소. detection 게이트 결정 후 진행 | §3.1, §5.2 |
| `vibe-thresholds-tune` | 3순위 (보류) | 분포가 합리적이라 임계값 자체 조정 시급성 낮음. 데이터 n 확장 후 재검토 | §2, §5.1 |
| `vibe-blind-spot-expand` | 보조 | "fork 또는 도구 자체" / "AI 문서 깊이 부재" 항목 추가. 옵션 결정 영향 적음 | §4.1, §5.4 |
| `non-roboco-validation-extended` | 데이터 확장 | n=9 → n≥15, Rust/C/Go 추가, 성숙 OSS (vue, django, rails) 추가 | §1 |

---

## 7. 본 변경에서의 코드 수정

design.md 결정 5 의 3 조건 (명백한 false positive / 1 함수 1–수 줄 / 회귀 없음) 을 모두 만족하는 즉시 수정 후보를 찾았으나 — **모두 임계값 변경 또는 신호 풀 변경 또는 detection 게이트 변경 영역** 에 속함. 본 변경에서는 코드 수정을 *적용하지 않고* 모두 후속 변경 제안으로 이관. 데이터 수집 + 권고 문서 작성으로 본 변경 범위 종결.

---

## 8. 검증 절차 spec 시나리오 자가 점검

본 결과 문서가 `vibe-coding-insights` capability 의 새 spec 시나리오를 모두 만족하는지:

- [x] 검증 데이터셋 다양성 매트릭스 — §1 에 명시 (언어 3 / 연령 1 차원만 / AI 도입 2 + 1 fork)
- [x] 검증 시 AI 호출 차단 — `scripts/validate_external_repos.py` 가 `ai_key_insight=None` 으로 호출
- [x] 검증 결과 문서 위치 — 본 파일 (`docs/validation/non-roboco-validation-results.md`)
- [x] 검증 데이터 raw 보존 — `docs/validation/non-roboco-data/*.json` 9 개

---

## 9. 한계

- n=9 는 분포 *경향* 관찰용. 가설 검정 아님. 임계값 변경의 통계적 유의성을 주장할 정도 아님.
- 성숙 OSS (≥ 5 년) 는 fastapi 1 개로 시도했으나 detection 탈락. 실제 분석 데이터는 모두 신생 레포.
- 비-AI OSS 는 fastapi 1 개. 옵션 A 채택 시 본 카테고리 자체가 의미 없으나, 옵션 B/C 검토 시 데이터 부족.
- AI narrative 품질은 평가 안 함 (결정 3). 별도 검증 변경 필요.

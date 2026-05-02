# CodeXray

[![PyPI](https://img.shields.io/pypi/v/codexray-wai.svg)](https://pypi.org/project/codexray-wai/)
[![CI](https://github.com/gusdh8380/CodeXray/actions/workflows/ci.yml/badge.svg)](https://github.com/gusdh8380/CodeXray/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

> 본인이 만든 vibe coding 프로젝트가 *주인이 있는 프로젝트* 인지 점검하고, **"다음에 무엇을 해야 할지"** 를 받아 보세요.

코드 분석 + AI 협업 흔적 진단 + 다음 행동 추천을 화면 하나에. AI 도구 (Claude Code · Codex CLI · Cursor 등) 로 코드를 만들어 본 적 있는 누구나 사용 가능합니다.

---

## 빠른 시작 (3 단계)

```bash
# 1. 설치
pip install codexray-wai

# 2. 실행
codexray serve

# 3. 브라우저가 자동으로 열립니다 → 분석할 폴더 선택
```

끝. 분석 결과가 나오면 *지금 뭘 해야 해* 카드만 보고 그대로 따라가시면 됩니다.

---

## 화면에서 보게 되는 것

### 1. 정체 — 이게 뭐야?
사람이 알아들을 수 있는 한 단락 요약. 메트릭 용어 (coupling, fan-in 같은) 없이 평어로.

### 2. 어떻게 만들어졌나
구조의 핵심 — 어떤 파일이 *시스템 전체를 붙잡고 있는지*, 진입점은 어디인지.

### 3. 지금 상태
4 차원 품질 등급 (A~F) + 위험도 가장 높은 파일 (변경 빈도 × 결합도).

### 4. 바이브코딩 인사이트 ★
*"주인이 있는 프로젝트"* 인지 3 축으로 진단:
- **의도** — 의도가 글로 박혔는가 (CLAUDE.md / docs/intent.md / pyproject description 등)
- **검증** — 결과를 사람이 직접 확인했는가 (validation 흔적 / 테스트 / examples)
- **이어받기** — 다음 세션이 이어받을 수 있는가 (회고 / 핸드오프 / 작은 PR)

각 축은 4 단계 상태 (`강함 / 보통 / 약함 / 판단유보`). 점수 (0–100) 는 일부러 안 보여줘요 — *정확해 보이는 숫자는 사용자를 오해시키니까*.

### 5. 지금 뭘 해야 해
0–3 개의 다음 행동 카드. 각 카드에 *Claude / Codex 에 그대로 복사할 prompt* 동봉. 비개발자도 새 AI 세션에 붙여 실행만 하면 됨.

화면 아래쪽엔 *이 도구가 못 보는 4 가지* 자가 점검 블록도 항상 노출 — 도구가 코드만 봐서는 못 잡는 차원 (의도의 깊이, 외부 도구의 기록 등) 을 *사용자가 직접 점검* 하라는 환기.

---

## Prerequisite

- **Python 3.11+** ([python.org](https://python.org) 또는 OS 패키지 매니저)
- **선택**: AI 정성 평가용 CLI — 둘 중 하나
  - **Codex CLI**: macOS `brew install --cask codex` · Windows `scoop install codex` · [공식 바이너리](https://github.com/openai/codex). ChatGPT Plus/Pro/Codex Plus 구독 활용
  - **Claude Code**: macOS `brew install claude-code` · Windows `winget install anthropic.claude-code`. Claude Pro/Max 구독 활용
- AI CLI 가 없어도 결정론 분석 (구조·등급·핫스팟·바이브코딩 진단) 까지 정상 동작. AI 가 만드는 *해석 narrative* 만 비활성.

---

## Vibe Coding 처음 시작하기

이 도구는 vibe coding 프로젝트의 *진단* 을 도울 뿐, vibe coding 자체를 배우려면 아래 권위 자료부터:

- **ROBOCO — [roboco.io](https://roboco.io/)** · 한국어 vibe coding 자료·도구 모음. 비개발자 학습자 1순위 시작점.
- **Anthropic — [Claude Code Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices)** · `CLAUDE.md` 의 역할과 작성 원칙
- **OpenAI Codex — [AGENTS.md guide](https://agents.md)** · `AGENTS.md` 형식 — CLAUDE.md 와 짝꿍 컨벤션
- **Andrej Karpathy — [vibe coding 용어의 출처](https://x.com/karpathy/status/1886192184808149383)** · 본 분야 명명자의 원본 정의
- **Simon Willison — [블로그 LLM 태그](https://simonwillison.net/tags/llms/)** · "Context is king", "Tests are non-negotiable"
- **Kent Beck — [Tidy First? Substack](https://tidyfirst.substack.com/)** · Constrain Context · Preserve Optionality · Maintain Human Judgment
- **Geoffrey Huntley — [ghuntley.com](https://ghuntley.com/)** · "한 번에 한 가지, 매 루프마다 계획"
- **Birgitta Böckeler (Thoughtworks) — [Exploring Generative AI](https://martinfowler.com/articles/exploring-gen-ai.html)** · "AI is an accelerator, not an automator"
- **Will Larson — [Theory of improvement (Irrational)](https://lethain.com/)** · 점수·등급의 한계와 *질적 진보* 의 본성
- **GitHub Spec Kit — [github/spec-kit](https://github.com/github/spec-kit)** · intent-driven development
- **Cursor / Cline / Aider** · Plan Mode · Memory Bank · `/undo` 패턴. [Cursor](https://www.cursor.com/) · [Cline](https://github.com/cline/cline) · [Aider](https://aider.chat/)

도구의 평가 기준도 이 자료들에서 합성됐습니다 (브리핑 화면 *"이 도구가 바이브코딩을 어떻게 평가하나요?"* 토글에 동일 출처).

---

## 자주 묻는 질문

**Q. 내 프로젝트가 vibe coding 으로 만든 게 아닌데도 분석되나요?**
→ 분석은 됩니다 (구조·품질·핫스팟). 다만 *바이브코딩 인사이트 섹션* 은 사라지고 4 섹션만 노출. 깔끔한 일반 OSS 분석 도구로 동작.

**Q. 평가 점수가 자꾸 약하게 나옵니다.**
→ 화면 아래 *"이 도구가 바이브코딩을 어떻게 평가하나요?"* 토글을 펼치고 8 운영 신호를 살펴보세요. 거의 항상 *외부화된 의도 (CLAUDE.md / 의도 문서)* 가 빠져 있습니다. 이게 vibe coding 의 가장 중요한 출발점입니다.

**Q. 결과가 신뢰할 만한가요?**
→ 외부 OSS 9 개로 검증된 신호 풀 (`docs/validation/non-roboco-validation-results.md`). 결정론 분석이라 같은 입력은 항상 같은 출력. AI 해석 부분은 별도 캐시에 분리 — *결정론 ≠ AI 정성* 명확히 분리됨.

**Q. 코드를 외부로 보내나요?**
→ **로컬 실행 우선**. AI 정성 평가만 본인의 codex/claude CLI 로 셸아웃. AI 안 쓰면 모든 분석이 100% 로컬.

---

## 개발자용 — 더 깊이

<details>
<summary>CLI 단독 명령 (10 개)</summary>

| 명령 | 출력 | 비용 |
|---|---|---|
| `codexray serve` | 웹 UI 띄움 (대부분 이거 한 줄로 충분) | 즉시 |
| `codexray dashboard <path>` | self-contained HTML 인터랙티브 대시보드 | ~2.4s |
| `codexray report <path>` | 1페이지 종합 Markdown + 룰 기반 권고 5 개 | ~2.4s |
| `codexray review <path>` | AI 정성 평가 JSON | 1~5 분 |
| `codexray inventory <path>` | 언어·파일·LoC 표 | ~0.5s |
| `codexray graph <path>` | 의존성 그래프 JSON (Py/JS/TS/C# type-resolved) | ~0.6s |
| `codexray metrics <path>` | fan-in/out · SCC · is_dag JSON | ~0.5s |
| `codexray entrypoints <path>` | 진입점 식별 JSON | ~0.5s |
| `codexray quality <path>` | 4 차원 등급 JSON | ~1.0s |
| `codexray hotspots <path>` | 변경 빈도 × 결합도 매트릭스 JSON | ~0.7s |

대상 언어: **Python · JavaScript · TypeScript · C#** (Java 후속).

</details>

<details>
<summary>환경변수</summary>

| 이름 | 기본값 | 설명 |
|---|---|---|
| `CODEXRAY_AI_BACKEND` | `auto` | `auto` (codex > claude 자동) / `codex` / `claude` 강제 |
| `CODEXRAY_AI_TOP_N` | `5` | `review` 명령이 처리할 hotspot 파일 수 |

</details>

<details>
<summary>git clone 방식 (소스 빌드)</summary>

```bash
git clone https://github.com/gusdh8380/CodeXray.git
cd CodeXray
uv sync
cd frontend && npm install && npm run build  # web UI 쓰려면 필수
uv run codexray serve
```

테스트 + 린트:
```bash
uv run pytest tests/ -q       # 320 tests
uv run ruff check
```

</details>

<details>
<summary>아키텍처 + 프로젝트 규약</summary>

```
src/codexray/
├── walk · language · loc · inventory     ← 파일 수집·언어 매핑
├── graph/ · metrics/ · entrypoints/      ← 의존성·메트릭·진입점
├── quality/ · hotspots/                  ← 등급·핫스팟
├── vibe_insights/                        ← 3 축 진단·신호 풀·9 룰 카드
├── briefing/                             ← 결정론 5 섹션 합성
├── web/                                  ← FastAPI + React SPA
├── ai/                                   ← codex/claude CLI 어댑터
└── cli.py                                ← typer 진입점 (10 서브커맨드)
```

`docs/` 에 의도·검증 결과·회고. `openspec/` 에 36 개 archived change. 모든 변경은 OpenSpec validate 게이트 통과 + 자기 적용 + 외부 OSS 검증 + 3 OS CI 통과.

설계 원칙 (`docs/constraints.md`): **로컬 실행 우선, AI 는 opt-in, 근거 라인 인용 필수, 사용자가 거절·재평가 가능**.

</details>

---

## Status

**Beta — `pip install codexray-wai` 설치 가능** (2026-05-02).

직전 큰 변경:
- `pypi-distribution` — PyPI 첫 publish
- `cross-platform-ci-setup` — 3 OS 자동 검증
- `vibe-signal-pool-expand` — 일반 OSS 신호 풀 확장 (5/9 외부 OSS 셀 개선)
- `vibe-detection-rebalance` — 비-AI 프로젝트는 vibe insights 섹션 자동 비노출
- `non-roboco-validation` — 외부 OSS 9 개 분석 결과 문서화
- `vibe-insights-realign` — 3 축 진단 + 4 단계 상태 + 9 룰 카드 + 평가 철학 토글

전체 history: [`openspec/changes/archive/`](openspec/changes/archive/), 검증 메모: [`docs/validation/`](docs/validation/), 회고: [`docs/vibe-coding/retro-2026-04-28.md`](docs/vibe-coding/retro-2026-04-28.md)

---

## License

MIT.

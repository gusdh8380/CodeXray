# CodeXray

로컬 코드베이스 분석 도구. 레포 경로 하나 입력하면 5섹션 브리핑 + 9개 미시 분석 탭 + 4개 구조 그래프 시각화 + 바이브코딩 3축 진단을 한 화면에서 보여준다.

## Tech Stack

- 백엔드: Python 3.14 + FastAPI + uvicorn + Typer (uv로 관리)
- 프론트엔드: React 19 + Vite + Tailwind v4 + shadcn-style 컴포넌트 + d3
- AI 어댑터: codex CLI 우선, claude CLI 폴백

## Development Commands

```bash
# 백엔드 테스트 (~5초, 322개 통과 기대)
uv run pytest tests/ -q

# 프론트엔드 빌드 (frontend/dist 생성, FastAPI가 정적 서빙)
cd frontend && npm install && npm run build

# 로컬 서버 실행 (http://127.0.0.1:8080)
uv run codexray serve --no-browser
```

## Coding Conventions

- 한국어 narrative (사용자 노출 텍스트). 메트릭 용어는 평어로 풀어 씀.
- 주석 최소. 의도가 자명한 코드는 주석 없음.
- 백엔드 변경 후 `uv run pytest tests/ -q`, 프론트엔드 변경 후 `npm run build` 필수 검증.
- 분석 변경 시 PROMPT_VERSION/SCHEMA_VERSION bump → 캐시 자동 무효화.

## Current Sprint

활성 OpenSpec 변경 없음.

직전 archive (2026-05-02): **`vibe-detection-rebalance`** — 옵션 A' 채택 (detection 게이트 유지 + 비감지 시 vibe insights 섹션 *통째로 비노출* + starter_guide 완전 제거). 두 페르소나 분리: 동료(자기 vibe 프로젝트)는 변화 없음, 본인(fastapi 같은 일반 OSS)은 깔끔한 일반 분석 도구로 변신. SCHEMA_VERSION 4→5 / ai_briefing 6→7 bump. `docs/validation/vibe-detection-rebalance-{self,fastapi}.md` 검증 통과.

다음 변경 후보:
- **vibe-signal-pool-expand**: pyproject description / examples / MAINTAINERS 등 신호 풀 확장. ROBOCO 컨벤션 의존도 추가 완화.
- **readme-vibe-coding-resources**: vibe coding 처음 시작하는 사용자를 위해 README 에 외부 자료 (Anthropic Best Practices, OpenAI AGENTS.md guide 등) 링크. starter_guide 제거 후 학습 진입점 보강.
- **bundle-composition-rebalance**: Python·AI 상호 검증 관계 (앵커링·long-tail·과번역 위험 — `docs/flow.md` 미래 섹션 참조).
- **cross-platform-distribution**: Windows/Linux 지원 + 설치 가이드.

이전 archive: 2026-05-01 `non-roboco-validation` (외부 OSS 9 개 검증), `vibe-insights-realign` (3축·4단계 상태·9 룰 엔진·평가 철학 토글). 2026-04-30 briefing-persona-split, briefing-rebuild, categorized-next-actions.

## Load on Demand

세부 문서는 필요할 때 읽기:

- `docs/intent.md` — 프로젝트 Why / What / Not (의도공학 1차 자료)
- `docs/flow.md` — 5 단계 동작 흐름 (결정론 분석 → 번들 → AI 호출 → 합성 → SPA)
- `AGENTS.md` — 에이전트별 역할 분리 (176줄)
- `openspec/changes/archive/2026-04-30-briefing-rebuild/` — 직전 대형 변경 (proposal/design/specs/tasks)
- `openspec/specs/` — 현재 capability spec (codebase-briefing, web-ui, react-frontend, vibe-coding-insights 등)
- `docs/validation/briefing-rebuild-self.md` — 최근 자체 검증 결과
- `docs/validation/briefing-rebuild-aquaview.md` — aquaview 레포 검증
- `docs/constraints.md` — 기술 제약
- `~/.cache/codexray/ai-briefing/` — AI 브리핑 캐시 (prompt_version로 키 분리)

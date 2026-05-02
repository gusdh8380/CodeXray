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

직전 archive (2026-05-02): **`cross-platform-ci-setup`** — GitHub Actions OS matrix CI 도입 (ubuntu/macos/windows). 사이클 1 회로 3 OS 모두 통과 (Windows 호환성 추가 fix 불필요 — 이미 잘 갖춰져 있던 결과). 발견된 fix 1 개: `test_main_page_serves_react_spa_when_dist_exists` 가 dist 부재 시 무조건 fail 했던 걸 `pytest.skipif` 로 조건부 처리. README 에 CI badge 추가. `docs/validation/cross-platform-ci-setup-results.md`. 후속 `pypi-distribution` 진입 가능.

다음 변경 후보:
- **pypi-distribution**: `pip install codexray` 한 줄 설치. pyproject 메타데이터 정비 + README OS 별 설치법 + (실제 publish 는 사용자 PyPI 토큰 필요).
- **bundle-composition-validation**: Python 결정론 결과가 AI 출력에 미치는 앵커링·long-tail·과번역 사례 데이터 수집. bundle-composition-rebalance 진입 전 입증.
- **vibe-thresholds-tune**: 70/40/10 임계값을 추가 데이터로 재검토 (n 확장 후).
- **frontend-ci**: CI matrix 에 `npm run build` 추가, frontend 회귀도 OS 별 자동 차단.

이전 archive: 2026-05-02 `vibe-signal-pool-expand` (신호 풀 일반 OSS 확장), `readme-vibe-coding-resources` (학습 자료 10 개), `vibe-detection-rebalance` (옵션 A'). 2026-05-01 `non-roboco-validation` (외부 OSS 9 개 검증), `vibe-insights-realign` (3축·4단계 상태·9 룰 엔진·평가 철학 토글). 2026-04-30 briefing-persona-split, briefing-rebuild, categorized-next-actions.

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

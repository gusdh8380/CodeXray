# Handoff to next agent (작성: Claude → Codex, 2026-04-28)

## TL;DR — 다음 작업

`add-web-ui` 변경 명세부터 시작. 사용자 결정 1개 대기 중 (프론트엔드 stack).

## 현재 스냅샷

- 12 changes / 14 commits, MVP 6개 feature 모두 출하 (`README.md`, `AGENTS.md` 참고)
- 233/233 pytest passing, ruff clean
- `git push` 완료: `git@github-personal:gusdh8380/CodeXray.git` main 브랜치
- 최근 commit: `d044ba0 docs: README rewrite + vibe-coding session retro`

## 사용자가 마지막으로 표명한 의도

> "지금 이 프로젝트를 사용하려면 명령어를 쳐야 하는데, 이거를 이제 UX/UI쪽으로 제어할 수 있게 하고싶어요"

8개 CLI 명령을 web UI로 묶기. 1인 도구이고 `constraints.md` 원칙은 "로컬 실행 우선, SaaS 호스팅 X".

## 결정된 사항

| 항목 | 결정 | 근거 |
|---|---|---|
| 새 명령 이름 | `codexray serve` | 다른 명령과 일관 |
| 백엔드 stack | **FastAPI** | 모던 Python, async, OpenAPI 자동, dep 무게 작음 |
| 호스팅 모델 | **localhost 단일 사용자** | constraints.md "로컬 실행 우선" |
| 자동 브라우저 열림 | yes (default) | UX 단순화 |
| 출력 형식 | 결과 패널에 inline (JSON pretty / Markdown 렌더 / HTML iframe) | tab 한 페이지 |
| AI review의 위치 | 별도 탭 + 명시 클릭 + 시간 경고 (1~5분) | opt-in 강조, constraints.md 정신 유지 |
| path 입력 UX | text input + localStorage로 최근 5개 history | 브라우저는 native folder picker 없음 |

## 미결정 (다음 메시지에서 사용자에게 확정 받을 것)

**프론트엔드 stack** — 사용자가 React를 물어본 상태에서 4 후보 중 선택 대기:

| 선택 | Build | 이 도구 1차 적합도 | 비고 |
|---|---|---|---|
| **htmx + Jinja2** | 없음 | ★★★★★ (추천) | 서버 주도, form→panel swap 패턴이 정확히 이 도구 흐름 |
| Alpine.js | 없음 | ★★★★ | HTML 속성 기반 state |
| Preact via CDN | 없음 | ★★★★ | React 멘탈 모델 + 빌드 0 |
| React + Vite | 있음 | ★★★ | 모던 DX, 1차에 무거움, 미래 확장 시 진정한 가치 |

추천 근거 (사용자에게 전달됨, 수락 안 됨):
- 이 도구 UI 복잡도는 "form + 8 tab + 결과 패널 + 로딩 상태" 수준
- 서버(FastAPI)가 이미 모든 분석 builder 보유 — 클라이언트는 swap만 하면 됨
- htmx는 그 swap 패턴을 한 줄(`hx-get="/api/inventory" hx-target="#panel"`)로 처리
- 빌드 파이프라인 0 = 기존 dashboard 패턴(단일 HTML + D3 CDN)과 일관

사용자가 React를 명시적으로 원하면 그 결정도 정당함 — **학습 의도** 또는 **미래 확장 가능성** (멀티 사용자, 클라우드 호스팅) 의 가치가 React 도입 비용을 정당화.

다음 응답에서 다시 4 후보 제시하고 1개로 확정 받기. 결정되면 곧장 `add-web-ui` proposal 작성으로 진행.

## 1차 단추 스코프 (스케치, 명세에서 확정)

**capability**: `web-ui` 신규

**CLI**: `codexray serve [--port 8080] [--no-browser]`

**구조** (FastAPI 가정):
```
src/codexray/web/
├── __init__.py
├── server.py          ← FastAPI app + 자동 브라우저 열림
├── routes.py          ← REST endpoints per builder (또는 Jinja fragment endpoints if htmx)
├── templates/         ← (htmx 채택 시) Jinja2 base.html, fragments.html
└── static/            ← 인라인 또는 별도 파일
```

**REST endpoints** (htmx 채택 시 fragments도 같은 URL로):
- `GET /` — 메인 페이지
- `POST /api/inventory` body `{"path": "..."}` → JSON 또는 HTML fragment
- `POST /api/graph`, `/api/metrics`, `/api/entrypoints`, `/api/quality`, `/api/hotspots`
- `POST /api/report` → Markdown rendered as HTML
- `POST /api/dashboard` → HTML iframe content
- `POST /api/review` → JSON (long-running, 스트리밍 또는 polling)

**UI 와이어프레임** (사용자가 동의한 형태):
```
┌─────────────────────────────────────────────┐
│  CodeXray  [path: ...]  [최근 ▼]  [Analyze] │
├──────────────┬──────────────────────────────┤
│ ▣ Overview   │                              │
│ ▣ Graph      │   결과 패널                  │
│ ▣ Metrics    │                              │
│ ▣ Hotspots   │                              │
│ ▣ Quality    │                              │
│ ▣ Entrypoints│                              │
│ ▣ Report     │                              │
│ ▣ Dashboard  │                              │
│ ▣ Review (AI)│   ⚠️ 명시 클릭 1~5분         │
└──────────────┴──────────────────────────────┘
```

## OpenSpec 명세 작성 시 주의

- `proposal.md`: 새 capability `web-ui`. Modified capability 없음.
- `design.md`: 프론트 stack 결정 + dependency 추가 (fastapi, uvicorn, [htmx면 jinja2도]) + REST 스키마 + 결정론·캐싱 정책 (path 같으면 같은 결과? 새 분석 강제?).
- `specs/web-ui/spec.md`:
  - "CLI 진입점", "포트 옵션", "자동 브라우저 열림", "8 endpoint 모두 작동", "AI review 명시 opt-in", "결과 캐싱 정책" 등
  - 각 endpoint 응답 스키마 명시 (모두 JSON 또는 HTML fragment)
  - 성능 예산: HTTP latency < 200ms (분석 자체는 builder의 5초 예산 그대로)
- `tasks.md`: server scaffold → routes → 템플릿/SPA 클라이언트 → 통합 → 테스트 → 검증

## 검증 게이트 (이전 변경들과 동일)

1. `openspec validate add-web-ui` 통과
2. `pytest -q` 회귀 0
3. `ruff check` clean
4. **자기 + CivilSim 두 트리에서 web UI 작동 확인** — `docs/validation/web-ui-{self,civilsim}.md`. UI는 시각이라 자동 검증 한계. 최소: HTTP endpoint smoke + 결과 schema 검증 + 사용자 직접 브라우저 열기.

## 환경 메모

- 사용자는 Codex Plus 구독 사용 → `codex` CLI 어댑터가 default
- Git identity: `~/Project/personal/` 아래는 gusdh8380(personal) 자동 (이번에 셋업 완료)
- 미해결 메모 (이번 세션에서 시작했지만 끝 못 본 것):
  - **gh CLI에 두 계정 모두 로그인** — 사용자가 인터랙티브 진행 중이었음. `gh auth status` 확인 필요. 이미 됐으면 OK, 아니면 `gh auth login --hostname github.com --git-protocol ssh --web` (gusdh8380으로 로그인) 진행 안내.
  - **direnv로 gh active account 디렉토리별 자동 전환** — 선택 사항, 사용자가 원하면 setup.
  - **CodeXray 과거 commit history 재작성** — 회사 email로 commit돼 있어 GitHub graph attribution이 회사 계정에 잡힘. 사용자가 personal로 옮기고 싶으면 `git rebase --root --exec '...amend --reset-author...'` + force-push. 안 해도 무방하면 그대로 유지.

## 핸드오프 시작 코맨드 (사용자에게 안내)

```
cd /Users/jeonhyeono/Project/personal/CodeXray
codex
```

Codex 첫 프롬프트로 던질 후보:
> "Read AGENTS.md and docs/handoff-to-codex.md, then propose the OpenSpec change `add-web-ui` after I confirm the frontend stack choice."

또는 사용자가 곧장 결정 알려주는 것도 OK:
> "Read AGENTS.md and docs/handoff-to-codex.md. Frontend는 htmx + FastAPI Jinja2로 갑시다. add-web-ui proposal부터 시작."

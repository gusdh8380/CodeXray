# briefing-rebuild — self validation (CodeXray)

**Date:** 2026-04-29
**Repo:** `/Users/jeonhyeono/Project/personal/CodeXray`
**Backend AI adapter:** codex
**Endpoint:** `POST /api/briefing` → `GET /api/briefing/status/{job_id}`

## SPA shell

`GET /` returns the React SPA shell:
- `<title>CodeXray</title>`
- `<div id="root"></div>` plus Vite-built `assets/index-*.js` and `assets/index-*.css`
- htmx-only landing markers (path-input, status-text, tab-button) absent

## Briefing payload (5 sections + vibe insights + actions)

`schema_version=2`, `ai_used=true`. Top-level metrics:

| metric | value |
|---|---|
| 파일 수 | 152 |
| LoC | 11,730 |
| 품질 등급 | D (52) |

### Section: 이게 뭐야 (what)

Narrative excerpt:

> CodeXray는 레포 경로를 입력하면 파일 구성, 의존성, 품질 등급, 변경 위험, 리포트, 대시보드, AI 정성 평가를 만들어 사용자가 '다음에 무엇을 해야 할지' 판단하게 돕는 로컬 코드베이스 분석 도구입니다.

`details.languages` returns 3 entries (Python 9,790 LoC / 83.5 %, TypeScript 1,917 LoC / 16.3 %, JavaScript 23 LoC / 0.2 %).

### Section: 어떻게 만들어졌나 (how_built)

Narrative excerpt:

> 152개 파일, 11,730 LoC 규모의 Python 중심 프로젝트이며, 핵심 흐름은 walk/inventory/graph가 원천 데이터를 만들고 metrics, quality, hotspots, report, dashboard, review가 이를 재사용하는 구조입니다. 그래프는 nodes 152, edges 712이지만 DAG=True이고 largest SCC=1이라 순환 의존은 사실상 없으며, 진입점은 pyproject의 codexray=codexray.cli:app와 cli.py의 Typer 명령, 그리고 serve를 통한 FastAPI 웹 UI입니다.

`details.top_coupled` returns 5 rows (top: `src/codexray/web/render.py` coupling 31). `details.entrypoints` returns 2 rows. `details.is_dag = true`.

### Section: 지금 상태 (current_state)

Narrative excerpt:

> 종합 품질은 D(52)로, 테스트는 B(75)라 회귀 방어는 어느 정도 있지만 문서화 F(4)와 결합도 D(58)가 사용성과 유지보수 리스크를 끌어내립니다. 특히 src/codexray/web/render.py는 changes 14, coupling 31, priority 434로 가장 위험한 핫스팟이며, 화면 렌더링·브리핑·JSON 패널·품질 해석이 한 파일에 몰려 있어 웹 UI 변경 때 파급 위험이 큽니다.

`details.dimensions` returns 4 entries (test B/75, cohesion B/87, coupling D/58, documentation F/4). `details.hotspots` returns 5 ranked rows.

### Section: 바이브코딩 인사이트 (vibe_insights)

`detected = true`, three axes:

| axis | score | label |
|---|---|---|
| environment | 100 | 환경 구축 |
| process | 60 | 개발 과정 깔끔함 |
| handoff | 85 | 이어받기 가능성 |

Weakest axis = process (Hotspot 84개 누적). Timeline reconstruction returns 4 events spanning 에이전트 지침 → 회고/인수인계 → OpenSpec 명세 → 검증 도입.

AI synthesis:

> 이 프로젝트의 핵심은 단순한 코드 메트릭 도구가 아니라 '정량 분석을 근거로 사람이 다음 결정을 내리게 하는 설명 계층'인데, 현재 위험도는 분석 엔진보다 그 결과를 웹에서 설명하고 조합하는 프레젠테이션 계층에 집중되어 있습니다.

### Section: 지금 뭘 해야 해 (next_actions)

3 structured triples (action / reason / evidence):

1. **render.py를 탭별 렌더러로 분리** — render.py priority=434, changes=14, coupling=31, fan_out=23
2. **routes.py 분석 실행 중복을 공유 파이프라인 또는 요청 캐시로 정리** — routes.py priority=243, changes=9, coupling=27
3. **CLAUDE.md/문서를 최신 명령·웹 UI·OpenSpec 절차로 갱신** — documentation F(4), 종합 품질 D(52)

## Micro-analysis JSON endpoints

| endpoint | result snapshot |
|---|---|
| `POST /api/quality` | overall D(52), dimensions: coupling, cohesion, documentation, test |
| `POST /api/hotspots` | summary: hotspot 84 / active_stable 64 / neglected_complex 1 / stable 3 (152 files total) |
| `POST /api/inventory` | 3 language rows (Python/TypeScript/JavaScript) |
| `POST /api/graph` | nodes 152, edges 712 |
| `POST /api/metrics` | 152 nodes including coupling stats |
| `POST /api/entrypoints` | typer entrypoint + cli.py |

All JSON endpoints return HTTP 200 within ~1 second on the validation host.

## SPA progress UX

Background job step transitions observed during a single run:

- `시작 중...` → progress 0.05
- `Python 분석 중...` → progress 0.20
- `AI 해석 중...` → progress 0.65
- `완료` → progress 1.0 (result attached)

No empty-screen state observed during the 30-90 second AI window.

## Summary

The rebuild produces meaningful, distinct narratives for each of the 5 sections, the vibe-coding three-axis evaluation correctly identifies process accumulation as the weakest area for this repo, and the next-action triples cite concrete files and metrics. Both the SPA shell and the JSON API endpoints answer within budget.

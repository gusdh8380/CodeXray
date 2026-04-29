# briefing-rebuild — aquaview validation

**Date:** 2026-04-29
**Repo:** `/Users/jeonhyeono/Project/personal/aquaview`
**Backend AI adapter:** codex
**Endpoint:** `POST /api/briefing` → `GET /api/briefing/status/{job_id}`

## Briefing payload (5 sections + vibe insights + actions)

`schema_version=2`, `ai_used=true`. Top-level metrics:

| metric | value |
|---|---|
| 파일 수 | 38 |
| LoC | 2,926 |
| 품질 등급 | C (64) |

### Section: 이게 뭐야 (what)

> AquaView는 수처리 시설의 센서 상태와 5단계 하수 처리 공정을 실시간으로 보여주는 풀스택 포트폴리오 MVP입니다. FastAPI가 센서·수질 시뮬레이션을 만들고, React 대시보드가 3초/10초 폴링으로 표시하며, Unity WebGL이 탱크·파이프 상태를 3D로 시각화합니다.

`details.languages`:
- C# 13 files, 1,227 LoC (41.9%)
- JavaScript 15 files, 1,089 LoC (37.2%)
- Python 10 files, 610 LoC (20.8%)

The AI correctly identifies the project domain (water-treatment monitoring), the architectural roles per stack (FastAPI sim, React dashboard, Unity 3D), and the polling cadence — all derived from reading CLAUDE.md / README and the actual source files attached in the bundle.

### Section: 어떻게 만들어졌나 (how_built)

> 전체 규모는 38파일, 2926 LoC이며 C# 13파일, JavaScript 15파일, Python 10파일로 백엔드·프론트엔드·Unity가 분리되어 있습니다. 의존 그래프는 nodes 38, edges 85이고 DAG=True, largest SCC=1이라 순환 의존은 없지만, React의 App.jsx가 여러 UI·API 흐름을 묶는 중심 허브입니다. 핵심 흐름은 FastAPI 시뮬레이터와 파이프라인 계산 결과가 REST API로 React에 들어오고, React가 iframe postMessage로 Unity WebGL에 SENSOR_UPDATE와 PIPELINE_UPDATE를 전달하는 구조입니다.

`details.top_coupled` (top 5):

| path | coupling |
|---|---|
| `frontend/src/App.jsx` | 12 |
| `backend/app/models.py` | 10 |
| `backend/app/simulator.py` | 8 |
| `unity/AquaView3D/.../ReadmeEditor.cs` | 6 |
| `frontend/eslint.config.js` | 5 |

`details.entrypoints` (top 5): all Unity lifecycle scripts (CameraController, DetailUI, PipeController, PumpAnimator, SensorDataReceiver).

### Section: 지금 상태 (current_state)

> 종합 품질은 C(64)로 MVP로는 이해 가능한 수준이지만, 테스트 등급 F(0)가 가장 큰 리스크입니다. 응집도 A(100), 결합도 B(88)는 구조 자체가 심하게 엉킨 상태는 아니라는 뜻이지만, hotspot 25개 중 App.jsx priority 72처럼 자주 바뀌고 연결도 높은 파일이 있어 작은 수정이 화면 전체 동작에 영향을 줄 수 있습니다. 특히 Unity3DView.jsx는 iframe 로드 후 3초/7초 재전송과 10초 폴링에 의존하므로 React-Unity 통신 실패를 테스트 없이 잡기 어렵습니다.

`details.dimensions`:

| dimension | grade | score |
|---|---|---|
| cohesion | A | 100 |
| coupling | B | 88 |
| documentation | C | 69 |
| test | F | 0 |

`details.hotspots` (top 5): `frontend/src/App.jsx` (priority 72) is the dominant hotspot.

### Section: 바이브코딩 인사이트 (vibe_insights)

`detected = true`, three axes:

| axis | score | label |
|---|---|---|
| environment | 53 | 환경 구축 |
| process | 25 | 개발 과정 깔끔함 |
| handoff | 0 | 이어받기 가능성 |

Weakest axis: handoff. Specifically there is no `docs/validation/`, `docs/vibe-coding/`, or `docs/handoff/`, and tests are F(0). Timeline reconstruction returns 1 event (`737a123 Initial commit`).

AI synthesis:

> 이 프로젝트의 핵심은 단순한 대시보드가 아니라 '수처리 공정 지식 → 시뮬레이션 → 2D/3D 시각 피드백'을 한 사용자 경험으로 묶은 점입니다. 구조는 아직 MVP답게 App.jsx와 Unity 브릿지에 오케스트레이션이 몰려 있지만, DAG=True와 cohesion A(100)를 보면 큰 재작성보다 중심 파일을 얇게 만들고 테스트를 붙이는 방향이 가장 효과적입니다.

### Section: 지금 뭘 해야 해 (next_actions)

3 structured triples:

1. **App.jsx를 데이터 조회 컨테이너와 화면 섹션 컴포넌트로 분리** — `frontend/src/App.jsx priority=72, changes=6, coupling=12`
2. **백엔드 시뮬레이터·파이프라인 API에 최소 회귀 테스트 추가** — `test 등급 F(0), backend/app/models.py coupling=10, backend/app/simulator.py coupling=8`
3. **React ↔ Unity postMessage 계약 명시 + 재전송 로직 상태 기반 정리** — `frontend/src/components/Unity3DView.jsx changes=6, SENSOR_UPDATE/PIPELINE_UPDATE`

Each action references concrete file paths and metrics from this repo, not generic advice.

## Cross-repo contrast (CodeXray vs aquaview)

| axis | CodeXray (self) | aquaview |
|---|---|---|
| environment | 100 | 53 |
| process | 60 | 25 |
| handoff | 85 | 0 |

The system meaningfully differentiates a mature vibe-coded repo (CodeXray, full agent infrastructure + handoff docs) from an early MVP that has only initial agent guidance (aquaview, no validation/retro/handoff). The same prompt + same backend produces qualitatively different next-action lists shaped by each repo's actual code and history.

## Summary

The rebuild reads aquaview's README + CLAUDE.md + source files and produces:
- Domain-correct project description ("수처리 시설", "5단계 하수 처리 공정")
- Architecture flow correctly identifying FastAPI ↔ React ↔ Unity messaging
- Concrete weakest-axis identification (handoff = 0) with actionable repair targets
- Test gap and App.jsx hub concentration both surfaced as evidence-backed actions

The 3-axis vibe-coding evaluation discriminates aquaview from CodeXray on every axis with sensible scores tied to file/test/doc evidence in each repo.

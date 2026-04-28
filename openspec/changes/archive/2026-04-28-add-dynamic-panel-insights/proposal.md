## Why

현재 web UI 우측 sidebar는 정적 한국어 텍스트로 채워져 있고 시니어 톤의 일반 설명을 담고 있다. 사용자의 원래 의도는 그것이 아니라 "지금 보고 있는 탭의 raw 분석 결과(JSON)를 시니어 개발자가 즉석에서 읽고 도출하는 인사이트"였다. 동시에 주니어 개발자를 위한 메트릭 학습 컨텍스트는 별도 패널로 항상 보이는 것이 옳다.

지금 구조는 두 의도를 한 곳에 섞어 둘 다 어중간하다. 시니어는 화면별 raw signal을 분석한 결과가 필요하고, 주니어는 그 메트릭이 무엇인지 학습할 정적 컨텍스트가 필요하다.

## What Changes

- 우측 sidebar를 두 패널로 분리한다.
  - **시니어 인사이트 (동적)**: 사용자가 명시 클릭하면 builder의 raw JSON을 codex/claude CLI 어댑터로 분석하여 3~5개 불릿(관찰 + 함의, 적어도 1개 risk + 1개 next-action) 인사이트를 생성한다. 백그라운드 job + polling + cancel.
  - **주니어 학습 컨텍스트 (정적)**: 기존 정적 한국어 설명을 유지하되 "이 메트릭이 무엇인지" 학습 톤으로 정제한다. 항상 표시되어 오프라인에서도 가용하다.
- 적용 탭: Overview, Inventory, Graph, Metrics, Entrypoints, Quality, Hotspots, Report. Dashboard는 raw가 HTML이라 본 변경에서 비활성화하고 design.md Open Question으로 두며, Review는 자체가 AI라 적용하지 않는다.
- 인사이트는 디스크 캐시로 결정론을 흉내낸다. 키 = `sha256(path | tab | raw_json_sha256 | adapter_id | prompt_version)`, 경로 = `~/.cache/codexray/insights/<key>.json`. 캐시 hit이면 즉시 반환, "다시 생성" 버튼이 강제 무효화한다.
- AI 어댑터 미설정/실패 시 시니어 패널에 안내 메시지만 표시되고 주니어 패널과 분석 결과는 영향받지 않는다.
- AI review의 background job + cancel 인프라(`web/jobs.py`)를 재사용한다.

## Capabilities

### New Capabilities

<!-- 해당 없음 -->

### Modified Capabilities

- `web-ui`: 결과 패널 우측 sidebar는 시니어 인사이트(AI 동적)와 주니어 학습 컨텍스트(정적) 두 영역으로 분리되어야 한다.
- `web-ui`: 시니어 인사이트는 raw JSON을 입력으로 codex/claude CLI 어댑터를 통해 명시 opt-in 백그라운드 job으로 생성되어야 한다.
- `web-ui`: 시니어 인사이트는 path + tab + raw JSON hash + adapter + prompt version 기반 디스크 캐시로 결정론을 흉내내야 하고 사용자가 재생성을 요청할 수 있어야 한다.
- `web-ui`: AI 어댑터가 사용 불가능하거나 호출이 실패할 때 web UI는 주니어 패널과 분석 결과를 그대로 유지해야 한다.

## Impact

- 변경 코드: `src/codexray/web/render.py`, `src/codexray/web/routes.py`, `src/codexray/web/jobs.py`, `src/codexray/web/templates/`, `src/codexray/web/static/app.css`
- 신규 파일: `src/codexray/web/insights.py` (prompt template + 안전장치 파서 + 디스크 캐시)
- 신규 디렉토리: `~/.cache/codexray/insights/` (사용자 home, 자동 생성)
- 의존성 추가 없음 (기존 `ai/adapters.py` 재사용)
- AI review의 background job 패턴 재사용
- CLI JSON schema 변경 없음

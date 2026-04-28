## Why

지금 분석 결과는 Python 템플릿이 하드코딩으로 즉시 표시한다. 수치는 나오지만 맥락이 없고, "발표 자료로 쓸 수 있는 웹 화면"이라는 Intent와 근본적으로 어긋난다. 규칙 기반 증거(fan-in, coupling, hotspot 등)를 수집하는 것은 Python이 잘 하지만, 그것을 사람이 이해하고 행동할 수 있는 언어로 바꾸는 것은 AI가 해야 한다.

## What Changes

- 분석 흐름이 변경된다: 경로 입력 → Python 증거 수집 → Claude CLI 해석 → 결과 웹페이지 표시
- 결과 페이지는 AI가 생성한 단일 종합 분석 — Briefing 방식이 전체 결과의 기본이 된다
- 로딩 중 진행 상태를 단계별로 표시한다 (단계마다 스트리밍 텍스트 업데이트)
- 기존 데이터 탭(Metrics, Hotspots, Quality 등)은 "근거 보기"로 접을 수 있게 유지
- 하드코딩된 해석 텍스트(coupling 위험도, LoC 레이블 등)는 AI 해석으로 대체

## Capabilities

### New Capabilities
- (없음)

### Modified Capabilities
- `web-ui`: 분석 결과 표시 방식을 하드코딩 즉시 렌더링에서 AI 해석 기반 단계적 로딩으로 전환
- `codebase-briefing`: 별도 탭이 아닌 모든 분석 차원(품질, 구조, 위험, 다음 행동)을 포괄하는 종합 결과로 확장

## Impact

- `src/codexray/web/render.py` — 주요 render 함수들을 AI 결과 표시로 교체
- `src/codexray/web/routes.py` — 분석 엔드포인트가 AI 호출 포함 비동기 흐름으로 변경
- `src/codexray/briefing/` — 증거 수집 범위를 전체 분석 지표로 확장
- `src/codexray/web/templates/` — 로딩 UX, 결과 레이아웃 변경
- 기존 테스트 `tests/test_web_ui.py` — 하드코딩 어서션 업데이트 필요

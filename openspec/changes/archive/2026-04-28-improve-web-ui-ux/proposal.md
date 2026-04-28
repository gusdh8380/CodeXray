## Why

`add-web-ui`로 localhost UI는 동작하지만, 초기 화면과 장기 실행 액션의 피드백이 약하다. 특히 AI review 실행처럼 시간이 걸리는 작업은 사용자가 멈춘 것으로 오해하기 쉽다. 1인 로컬 도구라도 "클릭했다 → 실행 중이다 → 결과가 왔다" 흐름은 명확해야 한다.

이번 변경은 분석 로직을 바꾸지 않고, 기존 htmx + Jinja2 UI의 상호작용 피드백과 첫 사용 경험을 개선한다.

## What Changes

- 첫 페이지 로드 후 Overview를 자동 실행한다.
- 선택한 탭을 active 상태로 표시한다.
- htmx 요청 중 result panel에 loading overlay를 표시한다.
- topbar에 짧은 status text를 표시한다.
- Review 실행 버튼은 클릭 즉시 disabled 상태가 되고 background job polling 상태를 명확히 보여준다.
- path 입력에서 Enter를 누르면 현재 active tab을 다시 실행한다.
- 오류 fragment는 시각적으로 더 명확하게 표시한다.

## Capabilities

### New Capabilities

<!-- 해당 없음 -->

### Modified Capabilities

- `web-ui`: existing localhost web UI SHALL provide clear loading, active navigation, first-load, and long-running review feedback.

## Impact

- 변경 파일: `src/codexray/web/templates/index.html`, `src/codexray/web/static/app.css`, `src/codexray/web/static/app.js`, `src/codexray/web/render.py`
- 테스트: main page marker, active/loading DOM hooks, review running fragment 검증 추가
- OpenSpec: `web-ui` spec의 UX 피드백 requirement 수정
- 의존성 추가 없음

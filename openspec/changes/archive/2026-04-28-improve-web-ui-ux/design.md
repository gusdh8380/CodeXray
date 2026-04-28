## Context

현재 UI는 htmx fragment swap 중심이다. 이 구조에서는 큰 프론트엔드 framework 없이도 `htmx:*` 이벤트와 작은 vanilla JS만으로 loading, active tab, first-load behavior를 구현할 수 있다.

## Goals / Non-Goals

**Goals:**
- 첫 화면에서 빈 패널 대신 Overview 자동 로드
- 클릭한 탭이 명확히 active로 보임
- 분석 요청 중 사용자가 기다리는 상태를 즉시 인지
- Review background job이 running/polling 상태를 명확히 표시
- path 입력 후 Enter로 현재 탭 재실행
- 기존 htmx + Jinja2 구조 유지

**Non-Goals:**
- React/Preact 도입
- WebSocket/Server-Sent Events 도입
- AI review 취소 버튼
- 분석 결과 캐시
- dashboard 내부 D3 UX 변경
- 새 분석 capability 추가

## Decisions

### Decision 1: htmx event hooks

`htmx:beforeRequest`, `htmx:afterRequest`, `htmx:responseError` 이벤트에서 active tab, loading state, status text를 갱신한다. htmx가 이미 요청 lifecycle을 제공하므로 별도 상태 관리 library는 필요 없다.

### Decision 2: Auto-load Overview

페이지 로드 후 Overview 버튼을 자동 click한다. 사용자는 바로 현재 repository 요약을 본다. path는 server template의 default path를 그대로 사용한다.

### Decision 3: Loading overlay inside result panel

요청 중 `.result-host`에 `is-loading` class를 붙이고 CSS pseudo overlay를 보여준다. 기존 결과를 유지한 채 loading만 덮기 때문에 화면이 튀지 않는다.

### Decision 4: Review running fragment is explicit

`render_review_running()`은 running message, job id 일부, polling text를 표시한다. htmx polling target은 계속 `#result-panel`로 유지한다.

### Decision 5: No new dependency

CSS/JS만 수정한다. 이 변경은 UX feedback이 목적이므로 dependency를 늘리지 않는다.

## Risks / Trade-offs

- **[리스크] htmx CDN 로드 실패**: 자동 Overview와 tab swap이 동작하지 않는다. 이는 기존 web-ui의 htmx CDN trade-off와 동일하다.
- **[리스크] auto-load가 큰 repo에서 즉시 분석을 시작**: Overview는 기존 validation에서 5초 내 완료한다. 사용자가 path를 바꾸면 Enter 또는 탭 클릭으로 재실행한다.
- **[트레이드오프] loading overlay가 기존 결과를 잠시 덮음**: 결과 유지보다 명확한 진행 피드백이 우선이다.

## Open Questions

- Review 취소 버튼은 후속 변경에서 job cancellation이 필요할 때 추가한다.

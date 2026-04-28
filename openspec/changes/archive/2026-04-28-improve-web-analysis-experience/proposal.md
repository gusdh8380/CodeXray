## Why

현재 web UI는 기능별 결과를 대부분 pretty JSON으로 보여준다. 이는 개발자 디버그 출력으로는 유용하지만, 사용자가 코드베이스 상태를 이해하고 다음 행동을 결정하기에는 가독성이 낮다. 주니어 개발자에게는 용어와 수치의 의미가 설명되어야 하고, 시니어 개발자에게는 hotspot, coupling, entrypoint, quality dimension을 빠르게 비교할 수 있는 깊이 있는 화면이 필요하다.

Dashboard도 iframe 안의 고정된 HTML을 넣는 방식이라 web UI 전체 흐름과 어긋나고 공간 활용이 나쁘다. AI review는 background job으로 바뀌었지만 중단할 수 없다.

## What Changes

- Overview, Inventory, Graph, Metrics, Hotspots, Quality, Entrypoints, Report의 기본 렌더링을 raw JSON에서 읽기 쉬운 HTML view로 바꾼다.
- 각 결과 view는 다음 구조를 갖는다.
  - 요약 cards
  - "What this means" 짧은 해석
  - 우선순위 table 또는 dimension breakdown
  - 필요 시 collapsible raw JSON
- Dashboard iframe은 고정 내부창 느낌을 줄이고 web UI result panel에 맞게 넓고 높은 분석 workspace로 표시한다.
- AI review running 화면에 Cancel 버튼을 추가한다.
- Review job은 cancelled 상태를 가질 수 있고, cancel 요청 후 status endpoint는 cancelled fragment를 반환한다.
- Light/Dark theme toggle을 추가하고 선택값을 localStorage에 저장한다.

## Capabilities

### New Capabilities

<!-- 해당 없음 -->

### Modified Capabilities

- `web-ui`: analysis results SHALL be rendered as human-readable decision views by default, with raw JSON available as secondary detail.
- `web-ui`: AI review background jobs SHALL support user-visible cancellation state.
- `web-ui`: theme SHALL support light/dark modes with persisted user preference.

## Impact

- 변경 코드: `src/codexray/web/render.py`, `src/codexray/web/routes.py`, `src/codexray/web/jobs.py`, `src/codexray/web/static/app.css`
- 테스트: readable panel markers, collapsible raw JSON, dashboard layout class, review cancel route/status
- 의존성 추가 없음
- React 전환 없음: 이번 문제는 framework 문제가 아니라 presentation 문제다. dashboard 자체가 더 복잡한 편집/필터링 app으로 확장될 때 React/Vite 변경을 별도 OpenSpec으로 검토한다.

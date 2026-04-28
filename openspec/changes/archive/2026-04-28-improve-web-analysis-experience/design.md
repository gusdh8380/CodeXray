## Context

CLI 명령의 JSON contract는 유지해야 한다. Web UI는 그 JSON을 사용자가 읽을 수 있는 정보 구조로 변환해야 한다. 따라서 serializer를 없애지 않고, web renderer에서 primary view와 raw detail을 함께 제공한다.

## Goals / Non-Goals

**Goals:**
- JSON dump를 기본 화면에서 제거하고 readable HTML을 기본으로 제공
- 주니어 개발자도 수치 의미를 이해할 수 있는 짧은 해석 제공
- 시니어 개발자가 빠르게 우선순위를 잡을 수 있는 table/rank 제공
- raw JSON은 `<details>`로 남겨 디버깅 가능하게 유지
- Dashboard iframe UX를 web UI 화면에 맞게 개선
- AI review cancel 버튼과 cancelled 상태 제공
- Light/Dark theme toggle 제공

**Non-Goals:**
- CLI JSON schema 변경
- React/Vite migration
- D3 dashboard algorithm rewrite
- AI subprocess hard-kill guarantee
- Multi-user job queue
- Database-backed job persistence

## Decisions

### Decision 1: Readable panels first, raw JSON second

모든 deterministic endpoint는 primary HTML view를 렌더링한다. raw JSON은 `<details class="raw-details">` 안에 둔다. 이로써 기존 debugging value는 유지하면서 기본 UX를 리포트형으로 바꾼다.

### Decision 2: Interpretation copy is deterministic

"What this means" 문구는 AI가 아니라 규칙 기반 정적 문구로 만든다. grade, coupling, hotspot category 같은 기존 정량 값에 따라 결정론적으로 출력한다.

### Decision 3: Tables for comparison

Inventory, graph nodes, metrics coupling, hotspots, entrypoints는 table이 가장 읽기 쉽다. 상위 N개를 기본으로 보여주고 raw JSON에서 전체를 확인한다.

### Decision 4: Dashboard panel sizing

iframe은 유지하되 카드 내부 preview가 아니라 full result panel workspace로 확장한다. max-width 제한을 해제하고 viewport 기반 높이를 늘린다. iframe 자체를 없애는 것은 dashboard HTML의 script/style 격리 문제 때문에 별도 변경으로 둔다.

### Decision 5: Cancel is cooperative

1차 cancel은 job state를 `cancelled`로 바꾸고 UI polling을 멈춘다. 이미 시작된 AI CLI subprocess를 강제 종료하는 것은 adapter 구조 변경이 필요하므로 후속 hard-cancel 변경으로 둔다. 단, cancelled job이 완료되어도 UI는 cancelled 상태를 유지한다.

### Decision 6: Theme toggle

초기 theme은 `localStorage`의 `codexray.theme.v1` 값을 우선하고, 없으면 `prefers-color-scheme`를 따른다. 버튼은 Light/Dark를 전환하고 `data-theme`을 `<html>`에 설정한다. CSS는 custom properties로 light/dark palette를 분리한다.

## Risks / Trade-offs

- **[리스크] Renderer 코드가 길어짐**: view helper를 작은 함수로 나눠 유지한다.
- **[리스크] Cooperative cancel은 비용을 즉시 중단하지 못함**: 사용자가 UI에서 대기를 중단할 수 있는 1차 UX 개선이며, subprocess kill은 후속 변경에서 adapter 레벨로 해결한다.
- **[트레이드오프] Dashboard iframe 유지**: 완전 통합보다 안전하고 빠르다. iframe 고정감은 CSS/layout으로 먼저 완화한다.
- **[리스크] Dashboard iframe 내부 theme 불일치**: 기존 dashboard HTML은 자체 스타일을 가진다. 외부 web UI theme과 완전 동기화는 후속 dashboard 변경에서 다룬다.

## Open Questions

- React migration은 dashboard filtering, graph interaction, compare view가 커질 때 별도 change로 평가한다.

## Why

Inventory, Graph, Metrics, Hotspots, Quality, Entrypoints, Report 화면은 이제 표와 요약을 제공하지만, 오른쪽 공간이 비어 있고 사용자가 수치의 의미를 스스로 해석해야 한다. 특히 주니어 개발자는 "그래서 이걸 보고 뭘 판단해야 하는가"가 필요하고, 시니어 개발자는 "어떤 리스크와 다음 행동을 볼 것인가"가 필요하다.

## What Changes

- Inventory, Graph, Metrics, Hotspots, Quality, Entrypoints, Report 패널에 오른쪽 설명 영역을 추가한다.
- 설명은 한국어로 작성하고, 시니어 개발자 관점의 해석 기준과 다음 행동을 담는다.
- 기존 요약 카드, 표, Raw JSON은 유지한다.
- 좁은 화면에서는 설명 영역이 본문 아래로 내려간다.
- Path 입력 옆에 Browse 버튼을 추가해 macOS Finder 폴더 선택으로 path를 채운다.

## Capabilities

### New Capabilities

<!-- 해당 없음 -->

### Modified Capabilities

- `web-ui`: analysis result panels SHALL include Korean contextual explanations for decision-making.
- `web-ui`: local web UI SHALL provide a macOS folder picker for path input when available.

## Impact

- 변경 코드: `src/codexray/web/render.py`, `src/codexray/web/static/app.css`
- 테스트: 분석 패널에 설명 영역과 한국어 문구가 포함되는지 확인
- 의존성 추가 없음

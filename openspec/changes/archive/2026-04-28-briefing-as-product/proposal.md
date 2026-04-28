## Why

지금 CodeXray는 12개 탭이 나란히 있는 "기능 모음집"이다. 사용자는 어느 탭을 봐야 할지 모르고, 비개발자가 열면 무엇부터 봐야 할지 전혀 알 수 없다. Intent의 핵심인 "웹 화면 자체가 발표 자료"를 달성하려면 구조 자체가 바뀌어야 한다. Briefing이 메인 결과 페이지가 되고 나머지는 뒤로 물러나야 한다.

## What Changes

- **"분석하기" 버튼 명확화**: 경로 입력 후 분석 시작이 명확한 단일 버튼으로 트리거됨. 지금처럼 탭을 클릭해야 분석이 시작되는 구조 제거.
- **Briefing이 메인 화면**: 분석 완료 후 첫 화면이 PPT 슬라이드형 Briefing. 7개 슬라이드 구성.
- **Vibe Coding 슬라이드 추가**: git 커밋 로그 + 프로젝트 폴더 구조를 바이브코딩 관점으로 분석해 잘한 것 / 못한 것 / 프로세스 인사이트를 별도 슬라이드로 표시.
- **나머지 탭 → 상세 보기**: Metrics, Hotspots, Quality, Graph, Inventory 등은 Briefing 하단 또는 별도 "상세 분석" 섹션으로 접어서 유지.
- **대시보드 수정**: 노드가 뷰포트 밖으로 나가는 문제 수정, 비주얼 개선 (bounded layout, 중요 노드 강조).

## Capabilities

### New Capabilities
- (없음)

### Modified Capabilities
- `web-ui`: 분석 시작 UX 변경, Briefing 메인화, 나머지 탭 상세보기 재배치, 대시보드 레이아웃 수정
- `codebase-briefing`: Vibe Coding 인사이트 슬라이드 추가 (잘한것/못한것/프로세스 근거)

## Impact

- `src/codexray/web/templates/index.html` — 탭 구조 전면 개편, "분석하기" 버튼 추가
- `src/codexray/web/static/app.js` — 분석 시작 로직 변경
- `src/codexray/web/static/app.css` — 상세보기 섹션, 대시보드 레이아웃 스타일
- `src/codexray/briefing/` — Vibe Coding 슬라이드 데이터 추가
- `src/codexray/web/render.py` — 상세보기 래퍼, Vibe Coding 슬라이드 렌더링
- `tests/test_web_ui.py` — UI 구조 변경에 따른 어서션 업데이트

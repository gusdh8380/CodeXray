## Context

현재 웹 UI는 Inventory 탭이 기본 활성 탭이다. Briefing 탭은 여러 탭 중 하나로 존재하며, 비개발자가 처음 접속하면 숫자 테이블이 먼저 노출된다. 또한 각 탭 하단에 `_raw_details` JSON 블록이 노출되고, insight 텍스트가 영어로 작성되어 있다.

Intent: "웹 화면 자체가 발표 자료로 쓸 수 있을 만큼 깔끔하다"

## Goals / Non-Goals

**Goals:**
- Briefing을 랜딩 뷰(기본 활성 탭)로 변경
- 탭 순서: Briefing → Overview → Inventory → Metrics → Quality → Hotspots → Report → AI Review
- 각 탭의 `_raw_details` JSON 블록 제거
- Insight 텍스트 영어 → 한국어 통일
- 상세 탭 그룹에 시각적 구분 추가 (선택적)

**Non-Goals:**
- 탭 자체의 콘텐츠 재설계 (별도 변경)
- 전문 용어 설명 추가 (별도 변경 B)
- 모바일 대응

## Decisions

### 1. 기본 탭 변경 방식
`GET /` 응답의 Jinja2 템플릿에서 초기 active 탭을 `briefing`으로 설정.
`app.js`의 자동 실행 로직도 `briefing`을 첫 번째로 트리거.

### 2. `_raw_details` 제거
`render.py`의 `_raw_details()` 호출을 각 render 함수에서 삭제.
함수 자체는 유지 (내부 디버그 목적으로 추후 재활용 가능).

### 3. Insight 텍스트 한국어화
`render_hotspots`, `render_review` 등의 `_insight()` 호출 내 영어 문자열을 한국어로 교체.

### 4. 탭 시각적 구분
Briefing + Overview는 "요약" 그룹, 나머지는 "상세 분석" 그룹으로 CSS divider 추가.
구현이 복잡하면 탭 순서 변경만으로 충분.

## Risks / Trade-offs

- `tests/test_web_ui.py`의 탭 순서 관련 어서션 업데이트 필요 — 누락 시 테스트 실패
- Briefing이 분석 완료 전에 열리면 빈 상태 노출 — 기존 로딩 UX 활용으로 처리

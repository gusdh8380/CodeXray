## 1. 헬퍼 함수 추가 (render.py)

- [x] 1.1 `_loc_label(loc: int) -> str` 추가 — LoC 규모 레이블 반환 (소규모/중규모/대규모/초대형)
- [x] 1.2 `_coupling_level(coupling: int) -> str` 추가 — 결합도 위험도 레이블 반환
- [x] 1.3 `_hotspot_category_kr(category: str) -> str` 추가 — 카테고리 한국어 변환

## 2. Inventory / Overview 인간화

- [x] 2.1 `render_inventory`: LoC 컬럼에 규모 레이블 추가 (예: "8,808 (중규모)")
- [x] 2.2 `render_overview`: LoC 메트릭 카드에 규모 레이블 추가

## 3. Metrics 탭 인간화

- [x] 3.1 테이블 컬럼 헤더 변경: "fan in" → "fan-in (의존받는 수)", "fan out" → "fan-out (의존하는 수)", "coupling" → "coupling (합계)"
- [x] 3.2 coupling 수치 컬럼에 위험도 레이블 추가

## 4. Hotspots 탭 인간화

- [x] 4.1 category 컬럼 값을 한국어로 변환 (hotspot→위험, active_stable→안정활성, neglected_complex→방치복잡, stable→안정)
- [x] 4.2 summary grid 카드 레이블 한국어화 ("Hotspots"→"위험", "Active stable"→"안정활성", "Neglected complex"→"방치복잡", "Stable"→"안정")

## 5. Quality 탭 인간화

- [x] 5.1 dimension 이름 한국어화 (coupling→결합도, cohesion→응집도, documentation→문서화, test→테스트)
- [x] 5.2 detail 컬럼의 raw dict 표현을 읽기 쉬운 형태로 변환

## 6. 검증

- [x] 6.1 `uv run pytest tests/ -x` 전체 통과 확인
- [x] 6.2 브라우저에서 Metrics/Hotspots/Quality/Overview 탭 확인 — 용어 설명이 표시되는지

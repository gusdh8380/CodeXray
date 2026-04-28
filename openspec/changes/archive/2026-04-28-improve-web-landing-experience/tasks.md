## 1. 탭 순서 및 기본 탭 변경

- [x] 1.1 Jinja2 템플릿에서 탭 순서를 Briefing → Overview → Inventory → Metrics → Quality → Hotspots → Report → AI Review 로 변경
- [x] 1.2 기본 활성 탭을 Briefing으로 변경 (HTML 초기 active 클래스 및 JS 자동 실행 대상)
- [x] 1.3 `tests/test_web_ui.py` 탭 순서 관련 어서션 업데이트

## 2. Raw JSON 제거

- [x] 2.1 `render_inventory`, `render_metrics`, `render_quality`, `render_hotspots`, `render_report` 함수에서 `_raw_details()` 호출 제거
- [x] 2.2 `render_review`, `render_graph`, `render_entrypoints` 함수에서 `_raw_details()` 호출 제거
- [x] 2.3 테스트에서 raw JSON 블록 관련 어서션 제거 또는 업데이트

## 3. Insight 텍스트 한국어화

- [x] 3.1 `render_hotspots` insight 텍스트 한국어로 교체
- [x] 3.2 `render_review` insight 텍스트 및 안내 문구 한국어로 교체
- [x] 3.3 기타 영어 insight/안내 문구 전수 확인 후 한국어화

## 4. 검증

- [x] 4.1 `uv run pytest tests/ -x` 전체 통과 확인
- [x] 4.2 `uv run codexray serve`로 직접 접속 — Briefing이 첫 화면으로 표시되는지 확인
- [x] 4.3 CodeXray 자기 자신에 분석 실행 후 raw JSON 노출 없는지 확인
- [x] 4.4 CivilSim 경로로 분석 실행 후 동일 확인

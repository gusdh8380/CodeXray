## 1. 패키지 스캐폴드

- [x] 1.1 `src/codexray/dashboard/__init__.py` — 공개 API
- [x] 1.2 `src/codexray/dashboard/types.py` — `DashboardData`

## 2. 빌더

- [x] 2.1 `dashboard/build.py` — `build_dashboard(root)`
- [x] 2.2 6개 builder 호출 (inventory + graph + metrics + entrypoints + quality + hotspots)
- [x] 2.3 generated_date = ISO-8601 로컬 타임존

## 3. HTML 템플릿 + 렌더러

- [x] 3.1 `dashboard/template.py` — `HTML_TEMPLATE` (string.Template)
- [x] 3.2 슬롯: title/path/date/grade/score/grade_class + 6 data
- [x] 3.3 v1 마커 헤더 5줄 안
- [x] 3.4 D3 v7 CDN script tag
- [x] 3.5 인라인 CSS — 헤더, 검색 박스, 그래프, 상세 패널, 범례, 등급 색상
- [x] 3.6 인라인 JS — 6 데이터 로드, force simulation, SVG 노드/엣지, 검색, 클릭 → 상세 패널
- [x] 3.7 `dashboard/render.py` — `to_html(data)`
- [x] 3.8 인라인 JSON 직렬화 (각 capability의 to_json + 인벤토리 직접 직렬화)

## 4. CLI 통합

- [x] 4.1 `cli.py`에 `dashboard` 서브커맨드
- [x] 4.2 경로 검증 재사용
- [x] 4.3 `build_dashboard` → `to_html` → `print`

## 5. 시각화 JS

- [x] 5.1 6 데이터 블록 로드 (`document.getElementById(...)textContent`)
- [x] 5.2 노드 변환 — graph.nodes + metrics.nodes(coupling) + hotspots.files(category, change_count) + entrypoints
- [x] 5.3 force simulation — link/charge/center/collide
- [x] 5.4 노드 SVG circle, 색상 = hotspot category, 반지름 = log(coupling+1)*4 + 4
- [x] 5.5 엣지 SVG line, 화살표 마커
- [x] 5.6 hover title — path + fan_in/fan_out
- [x] 5.7 노드 클릭 → 상세 패널 갱신 (path/language/coupling 분해/change_count/category/entrypoint_kinds)
- [x] 5.8 검색 input — opacity 필터링

## 6. 테스트

- [x] 6.1 v1 마커 + 6 인라인 JSON 블록 ID + D3 CDN tag + 헤더 데이터
- [x] 6.2 결정론 (date 고정)
- [x] 6.3 빈 트리 → N/A 표기
- [x] 6.4 CLI 통합 — 출력에 v1 마커 + data-graph
- [x] 6.5 6 인라인 JSON 모두 파싱 가능

## 7. 검증

- [x] 7.1 CodeXray 자기 자신 실측 — 0.95s, 96KB HTML, D(57) 등급. `docs/validation/dashboard-self.md` + `dashboard-self.html`
- [x] 7.2 CivilSim 실측 — 2.40s, 81KB HTML, D(40) 등급. `docs/validation/dashboard-civilsim.md` + `dashboard-civilsim.html`
- [x] 7.3 결과 HTML 파일을 `docs/validation/`에 영구 보관
- [x] 7.4 `openspec validate add-dashboard` 통과
- [x] 7.5 `ruff check` + `pytest` 모두 통과 (233/233)

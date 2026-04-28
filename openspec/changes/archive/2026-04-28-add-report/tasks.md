## 1. 패키지 스캐폴드

- [x] 1.1 `src/codexray/report/__init__.py` — 공개 API
- [x] 1.2 `src/codexray/report/types.py` — `Recommendation`, `ReportData`

## 2. 빌더

- [x] 2.1 `report/build.py` — `build_report(root)` 6 builder 호출
- [x] 2.2 inventory/graph/metrics/entrypoints/quality/hotspots 호출
- [x] 2.3 권고 생성 호출
- [x] 2.4 generated_date = ISO-8601 로컬 타임존

## 3. 권고

- [x] 3.1 `report/recommendations.py` — `generate(quality, metrics, hotspots, entrypoints)`
- [x] 3.2 룰: F 차원 (priority 80)
- [x] 3.3 룰: 사이클 (priority 60)
- [x] 3.4 룰: Top hotspot (priority 100)
- [x] 3.5 룰: D 차원 (priority 40)
- [x] 3.6 룰: 진입점 0개 (priority 20)
- [x] 3.7 정렬 + 5개 상한
- [x] 3.8 단위 테스트 — 룰별 / 우선순위 / 5개 상한 / 정렬

## 4. 렌더러

- [x] 4.1 `report/render.py` — `to_markdown(data)`
- [x] 4.2 헤더 + v1 마커
- [x] 4.3 Overall Grade 섹션 + 4행 표
- [x] 4.4 Inventory 섹션 + 표 (빈 트리 안내)
- [x] 4.5 Structure 섹션
- [x] 4.6 Top Hotspots 섹션 (최대 5)
- [x] 4.7 Recommendations 섹션
- [x] 4.8 단위 테스트 — 마커 1번 / 5섹션 헤더 / 빈 트리

## 5. CLI 통합

- [x] 5.1 `cli.py`에 `report` 서브커맨드
- [x] 5.2 경로 검증 재사용
- [x] 5.3 단위 테스트 — v1 마커, 5섹션 헤더, 구조 키워드

## 6. 검증

- [x] 6.1 통합 테스트 — 모든 섹션 + 권고
- [x] 6.2 결정론 회귀 (CLI 같은 입력 같은 출력 verified by deterministic_output 테스트들)
- [x] 6.3 CodeXray 자기 자신 실측 — 0.44s, overall D(57), 1순위 권고: cli.py hotspot. `docs/validation/report-self.md`
- [x] 6.4 CivilSim 실측 — 2.35s, overall D(40), 1순위 권고: GameManager.cs(15×45). `docs/validation/report-civilsim.md`
- [x] 6.5 `openspec validate add-report` 통과
- [x] 6.6 `ruff check` + `pytest` 모두 통과 (190/190)

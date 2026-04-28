## 1. 패키지 스캐폴드 + 점수 매핑

- [x] 1.1 `src/codexray/quality/__init__.py` — 공개 API
- [x] 1.2 `src/codexray/quality/types.py` — `DimensionScore`, `QualityReport`, `OverallScore`
- [x] 1.3 `src/codexray/quality/scoring.py` — `score_to_grade(score: float) -> str`
- [x] 1.4 단위 테스트 — 경계값 (90, 89, 75, 74, 60, 59, 40, 39, 100, 0)

## 2. Coupling 차원

- [x] 2.1 `src/codexray/quality/coupling.py` — `compute(graph) -> DimensionScore`
- [x] 2.2 internal 엣지에서 노드별 fan_in/fan_out 합산, 평균 → 점수 `100 - avg*10` clamp
- [x] 2.3 detail: `avg_fan_inout`, `max`
- [x] 2.4 빈 그래프 처리 — node_count=0이면 score=None
- [x] 2.5 단위 테스트 — 결합도 0(만점) / 평균 2 / max in detail / external 무시 / 빈 그래프

## 3. Cohesion 차원

- [x] 3.1 `src/codexray/quality/cohesion.py` — `compute(graph) -> DimensionScore`
- [x] 3.2 그룹화: 첫 2 디렉토리 segment, 부족하면 `(root)`
- [x] 3.3 그룹별 internal 엣지 카운트, 같은 그룹 내부 비율
- [x] 3.4 가중 평균 × 100
- [x] 3.5 internal 엣지 0이면 None
- [x] 3.6 단위 테스트 — 단일 그룹 / 두 그룹 교차 / 빈 internal / 루트 그룹

## 4. Documentation 차원

- [x] 4.1 `src/codexray/quality/documentation.py` — `compute(root) -> DimensionScore`
- [x] 4.2 Python AST: 모듈/함수/클래스 docstring 카운트
- [x] 4.3 C# 정규식: 클래스/메서드 선언 직전 `///` 주석 카운트
- [x] 4.4 items_total = Python + C# items, documented = 합산
- [x] 4.5 점수, items_total=0이면 None
- [x] 4.6 detail: `items_total`, `documented`
- [x] 4.7 단위 테스트 — Python 만점/절반/0 / C# /// / 0 items

## 5. Test 차원

- [x] 5.1 `src/codexray/quality/test.py` — `compute(root) -> DimensionScore`
- [x] 5.2 walk + classify로 소스 LoC
- [x] 5.3 테스트 디렉토리/파일명 식별 (`tests/`, `test_*.py`, `*Tests.cs`, `*.spec.ts` 등)
- [x] 5.4 ratio 계산
- [x] 5.5 점수 = `min(100, round(ratio * 200))`
- [x] 5.6 detail: `src_loc`, `test_loc`, `ratio`
- [x] 5.7 단위 테스트 — 0/만점/저비율/C# 패턴/TS spec/소스 0/Unity Tests dir

## 6. 빌더 + 직렬화

- [x] 6.1 `src/codexray/quality/build.py` — `build_quality(root)`
- [x] 6.2 `graph.build_graph` 호출 후 4차원 compute
- [x] 6.3 overall = non-null 평균 (모두 null이면 null)
- [x] 6.4 `quality/serialize.py` — `to_json` (들여쓰기 2)

## 7. CLI 통합

- [x] 7.1 `cli.py`에 `quality` 서브커맨드
- [x] 7.2 경로 검증 재사용
- [x] 7.3 단위 테스트 — JSON 파싱, 키 일관성, overall null

## 8. 검증

- [x] 8.1 통합 테스트 — 4차원 측정 가능 케이스 + 일부 N/A
- [x] 8.2 결정론 회귀
- [x] 8.3 CodeXray 자기 자신 실측 — 0.19s, overall D (58), 결과 `docs/validation/quality-self.md`
- [x] 8.4 CivilSim 실측 — 1.10s, overall F (32), 결과 `docs/validation/quality-civilsim.md`
- [x] 8.5 `openspec validate add-quality-quant` 통과
- [x] 8.6 `ruff check` + `pytest` 모두 통과 (150/150)

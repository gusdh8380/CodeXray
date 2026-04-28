## Context

분석 4개(인벤토리·그래프·메트릭·진입점)이 안정. 이번 변경은 그 위에 등급화 한 사이클. 1차는 명시적·결정론적 휴리스틱. 임계치는 동결하지 않고 design.md에 두어 후속 변경에서 자유롭게 조정.

## Goals / Non-Goals

**Goals:**
- 4차원 + 종합 등급 1회 산출
- AI 비의존, 결정론적, 회귀 테스트 쉬움
- 5초 예산 내
- 후속 변경(핫스팟·AI 평가)이 같은 JSON 위에 쌓일 수 있는 안정 스키마 v1

**Non-Goals:**
- 복잡도(cyclomatic, cognitive) — 별도 후속 변경
- 중복도(token-level diff) — 별도 후속 변경
- 보안 휴리스틱(eval, pickle, 하드코딩 비밀번호 패턴) — 별도 후속 변경
- 함수 단위 등급 — 1차는 차원별 점수만
- 사용자별 임계치 커스터마이즈 — 1차는 고정

## Decisions

### Decision 1: 별도 명령 (`quality`)
같은 패턴 (graph/metrics/entrypoints). 출력 스키마와 소비자가 다르다.

### Decision 2: 점수 → 등급 매핑 — 5등급 고정 임계치
```
score = 0..100
A = score >= 90
B = score >= 75
C = score >= 60
D = score >= 40
F = score < 40
```
**이유:** 학교 성적 친숙성 + 5단계가 비교 의사결정에 충분. 후속 변경에서 조정 가능.

### Decision 3: coupling 점수 — 평균 fan_in+fan_out 역수
- 파일별 `coupling_count = fan_in + fan_out` (internal 엣지만)
- 코드베이스 평균 `avg = sum(coupling_count) / node_count`
- 점수: `score = max(0, min(100, 100 - avg * 10))`
  - avg=0 → 100, avg=2 → 80, avg=5 → 50, avg=10 → 0
- detail에 `avg_fan_inout`, `max` 노출

**이유:** 단순·결정론적. 임계치 후속 조정 가능. 코드베이스가 작으면 평균만으로 분포 안 보이지만 1차에선 OK (max 같이 노출해 신호 보존).

### Decision 4: cohesion 점수 — 폴더 단위 내부 의존 비율
- "폴더"는 입력 루트 기준 첫 2단계 디렉토리 (예: `src/codexray/`, `Assets/Scripts/`)
- 한 폴더 내 모든 파일의 internal 엣지 중 **같은 폴더 내부로 가는 비율** = 폴더 응집도
- 그룹 = 깊이 2 폴더 + 그 미만(루트, 깊이 1)에 있는 파일은 단일 그룹 "(root)"
- 코드베이스 응집도 = 그룹 응집도의 가중 평균 (가중치는 그룹 내 파일 수)
- 점수: 응집도(0~1)에 100 곱
- detail: `groups_evaluated` (그룹 수)

**이유:** 폴더 = 1차 응집 단위. 깊이 2는 휴리스틱 (대부분 프로젝트의 모듈 단위와 일치). 후속 변경에서 namespace/패키지 기반으로 정밀화 가능.

### Decision 5: documentation 점수 — docstring/주석 비율
- **Python**: AST로 모듈/함수/클래스 노드 카운트, 그중 첫 statement가 `Expr(value=Constant(str))`인 비율 (= docstring 보유 비율)
- **C#**: 클래스/메서드 선언 직전 행에 `///` 시작 주석이 있는 비율
  - 클래스 정규식: `(public|internal|private|protected|sealed|static|abstract)?\s*(class|interface|struct|record|enum)\s+\w+`
  - 메서드 정규식: 한정자(public/private/...) + 반환타입 + 이름 + `(`
  - 직전 비공백 라인이 `///`로 시작하면 documented
  - 거짓양성/음성 가능 (정규식 한계). 1차 수용.
- **JS/TS**: 1차 비대상 (JSDoc 인식이 까다로움, 후속 변경)
- 코드베이스 `documentation_score` = (Python documented + C# documented) / (Python total + C# total) × 100
- detail: `items_total`, `documented`

### Decision 6: test 점수 — 테스트 LoC / 소스 LoC 비율
- 테스트 파일 식별:
  - 디렉토리 `tests/`, `test/`, `__tests__/`, `Assets/Tests/`, `Assets/Scripts/Tests/` 하위
  - 파일명 패턴: `test_*.py`, `*_test.py`, `*.test.ts`, `*.test.js`, `*.spec.ts`, `*.spec.js`, `*Tests.cs`, `*Test.cs`
- LoC는 `inventory.loc.count_nonempty_lines` 재사용
- ratio = test_loc / max(src_loc, 1)
- 점수: `min(100, ratio * 100 / 0.5)`
  - ratio=0 → 0, ratio=0.5 → 100. 0.5(=테스트 LoC가 소스 절반) 이상이면 만점
- detail: `src_loc`, `test_loc`, `ratio`

**이유:** 절대 LoC 비율은 거친 신호지만 결정론적. 테스트 품질(브랜치 커버리지 등)은 후속.

### Decision 7: overall 점수 — 단순 평균
- `overall_score = mean(coupling, cohesion, documentation, test)`
- `overall_grade = score_to_grade(overall_score)`

**이유:** 단순함이 1차 미덕. 후속에서 가중치 도입 (예: 큰 코드베이스에서 documentation 가중 낮춤).

### Decision 8: 패키지 구조 — `src/codexray/quality/`
- `quality/types.py` — `DimensionScore`, `QualityReport`
- `quality/scoring.py` — `score_to_grade(score: float) -> str`
- `quality/coupling.py`, `cohesion.py`, `documentation.py`, `test.py` — 각각 `compute(graph, ...) -> DimensionScore`
- `quality/build.py` — `build_quality(root) -> QualityReport`
- `quality/serialize.py`, `__init__.py`

각 차원 모듈을 분리해 후속 변경에서 차원 추가가 한 파일 추가로 끝나게.

### Decision 9: 입력 데이터 재사용
- `quality.build`는 `inventory.aggregate`와 `graph.build_graph`를 호출해 결과 활용
- 워킹은 두 번 (inventory 안 + graph 안). 1차에선 캐싱 안 함. 5초 예산 내라면 OK.
- 검증에서 5초 초과 시 캐싱 도입 후속

## Risks / Trade-offs

- **[리스크] 임계치 임의성** → design.md에 명시 + 후속 조정. 1차 결과의 절대값보다 **상대 비교**(자기 vs CivilSim)에 의미.
- **[리스크] 작은 코드베이스에서 분포 신호 약함** → CodeXray 자기 30개 노드라 평균값에 노이즈. 1차 수용.
- **[리스크] cohesion의 폴더 깊이 휴리스틱** → 평탄 구조(`src/`만 있는 트리)에서는 모두 한 그룹으로 묶여 100% 응집. CivilSim 같은 깊은 구조에서 의미 큼.
- **[리스크] documentation은 Python·C#만** → JS/TS 코드베이스에서 documentation 점수 산출 불가능. 1차에선 detail에 명시 (items_total=0이면 점수 100, 또는 점수 산출 skip).
- **[리스크] 워킹 두 번** → 같은 트리 두 번 walk. 큰 트리에서 비용 누적. CivilSim 50k pre-filter라도 walk 자체는 빠름. 검증으로 확인.
- **[트레이드오프] 종합 점수 단순 평균** → 작은 trees가 한 차원 박살나도 평균에 덜 반영. 1차 명시적.

## Open Questions

- documentation 점수 산출 시 JS/TS 파일이 0인지 아닌지 어떻게 처리할지 (현재: items_total=0 → 점수 산출 skip 또는 100? 1차에선 **N/A 표기 + 종합 평균에서 제외**, design.md에 명시)
- coupling의 max값을 점수에 반영할지 (현재는 detail로만 노출, 평균만 점수화)
- 후속에서 추가될 복잡도/중복도/보안 차원이 종합 점수에 어떻게 합쳐질지 (가중 평균?)

## Why

지금까지 만든 분석(인벤토리·그래프·메트릭·진입점)은 모두 입력 데이터다. 사용자가 의사결정에 필요한 "이 코드 어떻게 할까?"의 1차 답은 **등급**이다. AI 비의존 정량 등급 한 사이클을 먼저 만들고, AI 정성 평가(#3)·핫스팟(#4)이 같은 데이터 + 같은 등급 위에 쌓이게 한다. 1차에서 4차원(결합도·응집도·문서화·테스트)으로 좁히고, 복잡도·중복도·보안은 후속 변경에 떠넘긴다.

## What Changes

- 새 CLI 진입점: `codexray quality <path>` — 같은 walk + 그래프 한 번 빌드 + 4차원 점수 산출 → JSON 1개
- 4개 차원 + 코드베이스 종합 등급:
  - **coupling** (결합도): 파일별 `fan_in + fan_out`(internal). 낮을수록 좋음
  - **cohesion** (응집도): 폴더(첫 2단계 깊이) 단위, 그 폴더 안 파일들의 internal 엣지가 같은 폴더로 가는 비율. 높을수록 좋음
  - **documentation** (문서화): Python은 모듈/함수/클래스 docstring 비율 (AST), C#은 `///` 주석 비율 (정규식)
  - **test** (테스트): 테스트 파일 LoC / 소스 파일 LoC 비율 — 테스트 파일은 이름 패턴(`test_*.py`, `*_test.py`, `*Tests.cs`, `*.test.ts`, `*.spec.ts`) 또는 디렉토리 위치(`tests/`, `Assets/Tests/`)로 식별
- 각 차원 등급 매핑 (design.md에 임계치 테이블, 후속 변경에서 조정 가능):
  - A (90~100), B (75~89), C (60~74), D (40~59), F (<40)
- 출력 스키마 (스키마 v1, 신규 capability `code-quality`):
  ```json
  {
    "schema_version": 1,
    "overall": {"score": 72, "grade": "C"},
    "dimensions": {
      "coupling":      {"score": 80, "grade": "B", "detail": {"avg_fan_inout": 2.1, "max": 24}},
      "cohesion":      {"score": 65, "grade": "C", "detail": {"groups_evaluated": 6}},
      "documentation": {"score": 55, "grade": "D", "detail": {"items_total": 120, "documented": 66}},
      "test":          {"score": 88, "grade": "B", "detail": {"src_loc": 600, "test_loc": 480, "ratio": 0.80}}
    }
  }
  ```
- 사용 입력:
  - `inventory.aggregate(root)` 재사용 — LoC 데이터
  - `graph.build_graph(root)` 재사용 — internal/external 엣지
  - 새 카운트만 직접 계산 (docstring, 테스트 파일 분류)

## Capabilities

### New Capabilities
- `code-quality`: 코드베이스 정량 품질을 4차원(결합도·응집도·문서화·테스트)으로 점수화하고 A~F 등급으로 매핑해 JSON으로 노출하는 능력. 후속 변경(AI 정성 평가, 핫스팟, 종합 리포트)이 이 등급을 입력 또는 가중치로 받는다.

### Modified Capabilities
<!-- 해당 없음 -->

## Impact

- 신규 코드: `src/codexray/quality/` 서브패키지
  - `quality/scoring.py` — 점수 → 등급 매핑 (단일 함수)
  - `quality/coupling.py`, `cohesion.py`, `documentation.py`, `test.py` — 각 차원 점수 계산
  - `quality/build.py`, `serialize.py`, `types.py`
- 신규 의존성 없음 — 기존 graph/inventory/AST/정규식만
- 기존 동작 변경 없음 — `inventory`/`graph`/`metrics`/`entrypoints` 모두 그대로
- CLI에 `quality` 서브커맨드 추가
- 검증: CodeXray 자기 + CivilSim 두 트리에서 4차원 + overall 점수/등급 산출, 5초 내
- 1차 비대상: 복잡도(cyclomatic)·중복도·보안 — 별도 후속 변경

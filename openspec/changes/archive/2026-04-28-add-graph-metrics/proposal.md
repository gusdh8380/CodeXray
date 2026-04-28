## Why

`graph` 명령은 의존성 구조를 JSON으로 노출만 한다. 정량 평가(#2 MVP)는 결합도/응집도 등급을 내려면 fan-in/fan-out·강연결요소(SCC)·DAG 여부 같은 그래프 메트릭이 필요하다. 별도 그래프 계산 라이브러리(networkx 등)를 끌어들이지 않고, 표준 알고리즘(Tarjan SCC)을 직접 구현해 5초 예산 내에 메트릭을 산출한다. 후속 변경(품질 등급, 핫스팟)이 같은 메트릭 JSON을 입력으로 받게 한다.

## What Changes

- 새 CLI 진입점: `codexray metrics <path>` — 그래프를 1회 빌드하고 그 위에 메트릭 계산, JSON 1개 출력
- 출력 스키마(고정, 신규 capability):
  ```json
  {
    "schema_version": 1,
    "nodes": [
      {"path": "...", "language": "...", "fan_in": 3, "fan_out": 2, "external_fan_out": 5}
    ],
    "graph": {
      "node_count": 30,
      "edge_count_internal": 37,
      "edge_count_external": 66,
      "scc_count": 28,
      "largest_scc_size": 2,
      "is_dag": false
    }
  }
  ```
- 메트릭 정의:
  - **fan_in**: 그 노드를 가리키는 internal 엣지 수 (중복 엣지는 set 기반으로 1로 계수)
  - **fan_out**: 그 노드에서 다른 노드로 가는 internal 엣지 수
  - **external_fan_out**: 그 노드에서 external `to`로 가는 엣지 수
  - **SCC**: internal 엣지만 고려해 Tarjan 알고리즘으로 계산 (외부 모듈은 자기 자신만의 sink/source가 됨, SCC 계산 대상 아님)
  - **is_dag**: internal 엣지로 구성된 그래프가 DAG이면 `true` (모든 SCC 크기가 1이면 DAG)
- `codexray graph` 명령은 변경 없음 (메트릭은 별도 명령으로 격리)
- 새 모듈: `src/codexray/metrics/` 서브패키지
  - `metrics/scc.py` — Tarjan 알고리즘 (재귀 안 쓰고 명시 스택, 큰 그래프에서 stack overflow 회피)
  - `metrics/build.py` — Graph → MetricsResult
  - `metrics/serialize.py` — JSON 출력 (스키마 v1)
  - `metrics/types.py` — NodeMetrics, GraphMetrics, MetricsResult 데이터클래스

## Capabilities

### New Capabilities
- `code-metrics`: 의존성 그래프 위에서 노드별/그래프 단 정량 메트릭(fan-in/fan-out/SCC/DAG 여부)을 계산해 JSON으로 노출하는 능력. 후속 정량 평가(품질 등급, 핫스팟)의 입력 데이터 1차.

### Modified Capabilities
<!-- 해당 없음 — `dependency-graph`는 변경 없이 입력으로만 사용 -->

## Impact

- 신규 코드: `src/codexray/metrics/` 서브패키지 (4 파일 정도)
- 신규 의존성 없음 (Tarjan 직접 구현, 표준 라이브러리만)
- 기존 동작 변경 없음 — `inventory`/`graph` 명령은 그대로
- CLI에 `metrics` 서브커맨드 추가
- 검증: CodeXray 자기 + CivilSim 두 트리에서 메트릭 산출 확인, 예산 5초 내

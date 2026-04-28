# code-metrics Specification

## Purpose
TBD - created by archiving change add-graph-metrics. Update Purpose after archive.
## Requirements
### Requirement: 메트릭 CLI 진입점
The system SHALL expose a `codexray metrics <path>` command that prints a JSON metrics object to stdout. `<path>`는 위치 인수 1개로 필수이며, 추가 옵션 플래그는 받지 않는다.

#### Scenario: 정상 호출
- **WHEN** 사용자가 유효한 디렉토리 경로를 인수로 `codexray metrics <path>`를 실행하면
- **THEN** 시스템은 stdout에 단일 JSON 객체를 출력하고 종료 코드 0으로 종료한다

#### Scenario: 잘못된 경로
- **WHEN** 사용자가 존재하지 않는 경로 또는 디렉토리가 아닌 경로를 전달하면
- **THEN** 시스템은 stderr에 오류 메시지를 출력하고 종료 코드 0이 아닌 값으로 종료한다

#### Scenario: 인수 누락
- **WHEN** 사용자가 경로 인수 없이 `codexray metrics`를 실행하면
- **THEN** 시스템은 stderr에 사용법 메시지를 출력하고 종료 코드 0이 아닌 값으로 종료한다

### Requirement: 메트릭 JSON 스키마
The system SHALL emit JSON conforming to schema version 1 with top-level keys `schema_version`, `nodes`, and `graph`. `schema_version` MUST be the integer `1`. `nodes`는 배열이며 각 원소는 `path`(string), `language`(string), `fan_in`(int), `fan_out`(int), `external_fan_out`(int)를 포함한다. `graph` 객체는 `node_count`(int), `edge_count_internal`(int), `edge_count_external`(int), `scc_count`(int), `largest_scc_size`(int), `is_dag`(bool)를 포함한다.

#### Scenario: 스키마 키
- **WHEN** 임의의 유효한 코드베이스에 대해 `codexray metrics`를 실행하면
- **THEN** 출력 JSON 객체는 `schema_version`, `nodes`, `graph` 키를 모두 포함하고 `schema_version`은 정수 `1`이다

#### Scenario: 노드 객체 형식
- **WHEN** 출력 JSON에 노드가 포함될 때
- **THEN** 각 노드 객체는 `path`, `language`, `fan_in`, `fan_out`, `external_fan_out` 다섯 키만 포함한다

#### Scenario: 그래프 객체 형식
- **WHEN** 출력 JSON에 `graph` 객체가 있을 때
- **THEN** 그 객체는 `node_count`, `edge_count_internal`, `edge_count_external`, `scc_count`, `largest_scc_size`, `is_dag` 여섯 키만 포함한다

### Requirement: fan-in / fan-out 계산
The system SHALL compute `fan_in` as the count of distinct internal edges pointing TO the node and `fan_out` as the count of distinct internal edges originating FROM the node. `external_fan_out`은 그 노드에서 external `to`로 가는 엣지 수다. 동일 (from, to, kind) 쌍은 1로 계수된다 (그래프 단계에서 dedupe된 결과 사용).

#### Scenario: 단순 fan_out
- **WHEN** `a.py`가 internal 엣지로 `b.py`와 `c.py`로 가는 그래프
- **THEN** `a.py`의 `fan_out`은 2다

#### Scenario: 단순 fan_in
- **WHEN** `b.py`로 internal 엣지가 `a.py`, `c.py` 두 곳에서 들어오는 그래프
- **THEN** `b.py`의 `fan_in`은 2다

#### Scenario: external_fan_out 분리
- **WHEN** `a.py`가 internal 엣지로 `b.py`로 가고 external 엣지로 `os`, `sys`로 가는 그래프
- **THEN** `a.py`의 `fan_out`은 1, `external_fan_out`은 2다

#### Scenario: external 엣지로 향한 노드의 fan_in
- **WHEN** external 모듈 `os`로 들어가는 엣지가 트리에 여러 개 있을 때
- **THEN** `os`는 노드 객체로 등장하지 않으며 어떤 노드의 `fan_in`도 그 엣지로 증가하지 않는다 (external 노드는 메트릭 대상 아님)

### Requirement: SCC 계산
The system SHALL compute strongly connected components on the internal-edge subgraph using Tarjan's algorithm with an explicit stack (no recursion). 외부 엣지는 SCC 계산 대상이 아니다. 결정론적 출력을 위해 노드 순회 순서는 `path` 사전순으로 고정한다.

#### Scenario: 빈 그래프
- **WHEN** 트리에 분석 대상 파일이 없을 때
- **THEN** `scc_count`는 0이고 `largest_scc_size`는 0이며 `is_dag`는 `true`다

#### Scenario: DAG 체인
- **WHEN** internal 엣지가 `a.py → b.py → c.py` 직선이고 cycle이 없을 때
- **THEN** `scc_count`는 3, `largest_scc_size`는 1, `is_dag`는 `true`다

#### Scenario: 단순 사이클
- **WHEN** internal 엣지가 `a.py → b.py → a.py`로 cycle을 이룰 때
- **THEN** `scc_count`는 1 (a, b가 한 SCC), `largest_scc_size`는 2, `is_dag`는 `false`다

#### Scenario: 혼합 (DAG 일부 + SCC 일부)
- **WHEN** 트리에 노드 4개 — `a → b → c → b` (b, c가 cycle), `d`는 isolated
- **THEN** `scc_count`는 3 (`{a}`, `{b, c}`, `{d}`), `largest_scc_size`는 2, `is_dag`는 `false`다

### Requirement: 그래프 단 카운트
The system SHALL include `node_count` (분석 대상 internal 노드 수), `edge_count_internal` (distinct internal 엣지 수), and `edge_count_external` (distinct external 엣지 수) under the top-level `graph` object.

#### Scenario: 카운트 일관성
- **WHEN** 임의의 트리에 대해 `codexray metrics`를 실행하면
- **THEN** `graph.node_count`는 `nodes` 배열 길이와 같고, `graph.edge_count_internal`은 모든 노드의 `fan_out`의 합과 같으며, `graph.edge_count_external`은 모든 노드의 `external_fan_out`의 합과 같다

### Requirement: 결정론적 정렬
The system SHALL sort the `nodes` array by `path` ascending. SCC 처리 순서가 출력에 영향을 주지 않도록 노드 enumerate 순서도 `path` 사전순으로 고정한다.

#### Scenario: 동일 입력 동일 출력
- **WHEN** 동일한 입력 트리에 대해 `codexray metrics`를 두 번 실행하면
- **THEN** 두 실행의 stdout 바이트가 완전히 동일하다

### Requirement: 성능 예산
The system SHALL complete metrics output within 5 seconds on the validation codebases (CodeXray repo, CivilSim).

#### Scenario: 검증 코드베이스
- **WHEN** 검증용 코드베이스에 대해 `codexray metrics`를 실행하면
- **THEN** 시스템은 5초 이내에 JSON 출력을 완료한다


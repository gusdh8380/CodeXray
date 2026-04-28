## Context

`add-dependency-graph`+`add-graph-csharp`가 끝난 시점. CodeXray 자기 30 nodes / 37 internal, CivilSim 53 nodes / 457 internal. 두 트리 모두 노드 수가 작아 O(V+E) 알고리즘이면 메트릭 계산은 무시할 수 있는 비용. 외부 의존성(networkx)을 들이지 않고 표준 알고리즘(Tarjan SCC) 직접 구현으로 충분.

## Goals / Non-Goals

**Goals:**
- 그래프 → 메트릭 변환을 결정론적으로 1회 패스
- 후속 분석(품질 등급, 핫스팟)이 받을 안정적 JSON 스키마 v1 확정
- 5초 예산 내 (그래프 빌드 0.66s + 메트릭 계산 < 0.1s 예상)
- 기존 `graph` 명령 무영향

**Non-Goals:**
- 정밀 중심성(betweenness, eigenvector, PageRank) — 계산 비용 큼, 후속
- 모듈/폴더 단위 응집도 — 노드를 폴더로 그루핑하는 결정이 따로 있어야 함, 후속
- 외부 의존(npm/pip 패키지) 메트릭 — 외부 모듈 그래프는 1차 비대상
- 그래프 시각화·표 출력 — JSON만
- networkx 같은 외부 라이브러리 도입

## Decisions

### Decision 1: 별도 명령 (`metrics`) vs `graph --with-metrics`
**선택:** 별도 명령 `codexray metrics`.
**이유:** 출력 스키마가 다르고(`graph`는 nodes/edges, `metrics`는 nodes(증강)/graph(전체)) 소비자도 다르다. 한 명령에서 옵션으로 형태 분기는 후속 분석 단계의 결합을 키우는 안티패턴. 별도 명령이 깔끔.

### Decision 2: SCC 알고리즘 — Tarjan (반복형)
- 클래식 알고리즘, O(V+E)
- 재귀 깊이 폭증 회피 위해 **명시 스택 기반 반복 구현**
- 노드 정렬: `path` 사전순으로 enumerate해 결정론적 출력 보장
- 외부 노드는 SCC 대상 아님 (internal 엣지만 그래프 구성)

**대안 기각:** Kosaraju (2회 DFS). Tarjan과 복잡도 동일하나 코드량은 비슷, Tarjan이 더 익숙. networkx 도입은 라이브러리 비용 대비 SCC 하나에 과함.

### Decision 3: fan-in/fan-out 정의
- **internal만 카운트** — fan-in/fan-out은 1차 의존성 그래프 내부 결합도를 본다
- external 사용량은 별도 컬럼 `external_fan_out`로 분리
- 중복 엣지(`graph` 출력에는 set 기반이라 없음)가 들어와도 set으로 한 번 더 dedupe

### Decision 4: `is_dag` 정의
- internal 엣지만 고려한 directed graph가 cycle이 없으면 true
- 구현: 모든 SCC의 size가 1이면 DAG
- self-loop는 cycle (size 1 SCC라도 self-edge가 있으면 DAG 아님) — 1차에서는 self-edge 가능성을 인정하지 않음 (`graph`가 만들 일 거의 없음). spec scenario에 자세히 명시.

### Decision 5: 스키마 v1 — `graph` 스키마와 분리
- `metrics` JSON의 `schema_version`은 독립 (1로 시작)
- `graph` JSON과 다른 capability(`code-metrics`)에 속한다
- 후속 변경에서 추가될 메트릭은 v1에 키만 더하기(추가는 호환), 기존 키 의미 변경은 v2

### Decision 6: 결정론
- nodes 정렬: `path` 사전순
- SCC 사이즈 통계만 노출 (`scc_count`, `largest_scc_size`); 멤버십 노드 list는 1차 비공개 (스키마 단순화)
  - 후속에서 `largest_scc_members: [path...]` 같은 필드 추가 가능 (v1 호환)

### Decision 7: 패키지 구조 — `src/codexray/metrics/`
- `metrics/types.py` — NodeMetrics, GraphMetrics, MetricsResult
- `metrics/scc.py` — `tarjan_scc(adj: dict[str, list[str]]) -> list[set[str]]`
- `metrics/build.py` — `build_metrics(graph: Graph) -> MetricsResult`
- `metrics/serialize.py` — `to_json(metrics: MetricsResult) -> str`
- `metrics/__init__.py` — public API 노출

`graph` 패키지와 같은 컨벤션, 후속 변경에서 메트릭 추가 시 일관성 유지.

### Decision 8: 입력 — `build_graph(root)` 재사용
- 메트릭은 그래프를 입력으로 받기 때문에 `build_graph(root)`를 호출해 같은 노드/엣지를 얻고, 그 위에 메트릭만 더한다
- `metrics` 명령 내부에서 `Graph` 인스턴스를 직접 만든다. 외부 JSON을 stdin으로 받는 방식은 후속 변경(파이프라이닝)에서 검토.

## Risks / Trade-offs

- **[리스크] 큰 SCC가 등장하는 트리에서 알고리즘 정확성 회귀** → 반복형 Tarjan은 재귀형보다 코드 복잡도 살짝 높다. 단위 테스트로 5종 시나리오(빈 그래프 / 단일 노드 / DAG 체인 / 단순 사이클 / 복합 SCC) 커버.
- **[트레이드오프] SCC 멤버십 미공개** — 1차 스키마 단순화. 사용자가 큰 SCC를 들여다보고 싶을 때 별도 명령 또는 v1 추가가 필요. 1차 의도된 단순화.
- **[리스크] 외부 의존 카운트가 부풀려짐** — 거짓 import(JS 정규식 한계)도 external_fan_out에 포함. `graph` 단계의 한계 그대로 상속. 명세에 표기.
- **[리스크] CodeXray 자기 자신은 작아 SCC가 거의 없음** → CivilSim 검증에서 SCC 통계가 의미 있는지 확인. 의미가 없다면 후속 변경에서 큰 트리 검증 필요.

## Open Questions

- 후속에서 `largest_scc_members`를 추가할지, 별도 명령 `codexray metrics --explain-scc`로 분리할지 — 데이터가 들어왔을 때 결정
- 모듈 단위(폴더) 메트릭은 폴더 그루핑 정책이 따로 필요 — 별도 변경

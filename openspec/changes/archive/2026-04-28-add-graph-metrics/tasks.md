## 1. 패키지 스캐폴드

- [x] 1.1 `src/codexray/metrics/__init__.py` — 공개 API: `build_metrics`, `to_json`, 데이터클래스
- [x] 1.2 `src/codexray/metrics/types.py` — `NodeMetrics(path, language, fan_in, fan_out, external_fan_out)`, `GraphMetrics(...)`, `MetricsResult(schema_version, nodes, graph)` (frozen, slots)

## 2. SCC 알고리즘

- [x] 2.1 `src/codexray/metrics/scc.py` — `tarjan_scc(adj: dict[str, list[str]]) -> list[set[str]]`
- [x] 2.2 반복형 (재귀 X) — 명시적 스택 사용, 큰 트리에서 stack overflow 방지
- [x] 2.3 노드 enumerate 순서: 입력 dict의 키를 정렬해 결정론
- [x] 2.4 단위 테스트 — 빈 그래프 / 단일 노드 / DAG 체인 / 사이클 2-노드 / 사이클 3-노드 / 혼합(DAG+SCC) / 자기 루프 (size 1 SCC)

## 3. 메트릭 빌더

- [x] 3.1 `src/codexray/metrics/build.py` — `build_metrics(graph: Graph) -> MetricsResult`
- [x] 3.2 노드별 fan_in/fan_out: 그래프 엣지 set에서 internal만 dedupe 카운트
- [x] 3.3 노드별 external_fan_out: external 엣지에서 from별 카운트
- [x] 3.4 internal-only adjacency 구성, `tarjan_scc` 호출
- [x] 3.5 `scc_count`, `largest_scc_size`, `is_dag` 도출 — `is_dag = all(len(scc) == 1 and no_self_loop(scc) for scc in sccs)`
- [x] 3.6 단위 테스트 — fan_in/fan_out 단순 케이스 / external 분리 / external 노드는 메트릭 대상 X

## 4. 직렬화

- [x] 4.1 `src/codexray/metrics/serialize.py` — `to_json(metrics: MetricsResult) -> str` (들여쓰기 2, ensure_ascii=False)
- [x] 4.2 노드 정렬은 `path` 사전순
- [x] 4.3 단위 테스트 — 스키마 키 존재 / 결정론 (같은 입력 두 번 호출 동일 출력)

## 5. CLI 통합

- [x] 5.1 `src/codexray/cli.py`에 `metrics` 서브커맨드 추가
- [x] 5.2 경로 검증은 `_validate_dir` 재사용
- [x] 5.3 정상 흐름 — `build_graph(target)` → `build_metrics(graph)` → `to_json` → `print`
- [x] 5.4 단위 테스트 — `typer.testing.CliRunner`로 임시 트리에 대해 JSON 파싱 가능성·키 존재·일관성(node_count == len(nodes)) 검증

## 6. 검증

- [x] 6.1 통합 테스트 — Python 자기참조 픽스처에서 fan_in/fan_out 정확성 + SCC 0 사이클 케이스 검증
- [x] 6.2 통합 테스트 — 강제 사이클 픽스처(`a → b → a`)에서 `scc_count`, `is_dag=false` 검증
- [x] 6.3 결정론 회귀 — 같은 트리 두 번 실행 stdout 바이트 일치
- [x] 6.4 CodeXray 자기 자신 실측 — 38 nodes / 50 internal, is_dag=true, top fan_in `graph/types.py`(10). `docs/validation/metrics-self.md`에 캡처
- [x] 6.5 CivilSim 실측 — 0.49s, 53 nodes / 457 internal, **largest_scc_size=15, is_dag=false** (사이클 발견). `docs/validation/metrics-civilsim.md`에 캡처
- [x] 6.6 `openspec validate add-graph-metrics` 통과 재확인
- [x] 6.7 `ruff check` + `pytest` 모두 통과 (89/89)

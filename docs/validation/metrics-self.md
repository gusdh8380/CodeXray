# Metrics — CodeXray 자기 검증

**Change:** `add-graph-metrics`
**Run date:** 2026-04-28 (KST)
**Target:** `/Users/jeonhyeono/Project/personal/CodeXray`

## Result

```
$ uv run codexray metrics .
{
  "schema_version": 1,
  "graph": {
    "node_count": 38,
    "edge_count_internal": 50,
    "edge_count_external": 79,
    "scc_count": 38,
    "largest_scc_size": 1,
    "is_dag": true
  }
}
```

| metric | value |
|---|---|
| nodes | 38 |
| internal edges | 50 |
| external edges | 79 |
| SCCs | 38 (모두 size 1) |
| largest SCC | 1 |
| **is_dag** | **true** |

## Top fan_in (가장 많이 import되는 모듈)

| path | fan_in | fan_out | external |
|---|---|---|---|
| src/codexray/graph/types.py | 10 | 0 | 3 |
| src/codexray/graph/__init__.py | 4 | 3 | 0 |
| src/codexray/cli.py | 3 | 4 | 4 |
| src/codexray/inventory.py | 3 | 3 | 5 |
| src/codexray/language.py | 3 | 0 | 2 |

## Top external_fan_out (외부 의존이 많은 모듈)

| path | external |
|---|---|
| src/codexray/graph/csharp_index.py | 5 |
| src/codexray/inventory.py | 5 |
| src/codexray/walk.py | 5 |

## Performance

| metric | value |
|---|---|
| wall (`real`) | **0.28s** |
| user | 0.12s |
| sys  | 0.05s |
| budget | 5.00s |
| margin | ≈ 18× under budget |

## Observations

1. **DAG 확인** — 자기 자신 의존성 그래프가 사이클이 없다. Python 패키지 구조가 깔끔하다는 신호.
2. **`graph/types.py` 중심성 최고 (fan_in=10)** — 데이터클래스 모듈이 다른 graph 서브모듈에 의해 가장 많이 참조됨. 합리적 (types가 안정적이어야 함).
3. **`graph/__init__.py` (fan_in=4)** — public API export 모듈. tests가 이걸 통해 import. 변경 시 회귀 위험 큰 모듈로 식별됨.
4. **메트릭 빌드 비용 무시할 수 있음** — 그래프 빌드 자체가 0.21s였는데 메트릭까지 포함 0.28s. SCC + 카운트 추가 비용 ≈ 0.07s.

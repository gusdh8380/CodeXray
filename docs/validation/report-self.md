<!-- codexray-report-v1 -->
# CodeXray Report — `/Users/jeonhyeono/Project/personal/CodeXray`
**Date:** 2026-04-28

## Overall Grade: D (57)

| dimension | grade | score | detail |
| --- | --- | --- | --- |
| coupling | C | 63 | avg_fan_inout=3.65, max=16 |
| cohesion | D | 59 | groups_evaluated=2 |
| documentation | F | 5 | documented=21, items_total=397 |
| test | A | 100 | ratio=0.88, src_loc=1816, test_loc=1606 |

## Inventory

| language | file_count | loc | last_modified_at |
| --- | --- | --- | --- |
| Python | 81 | 3422 | 2026-04-28T10:20:19+09:00 |

## Structure

- nodes: 81
- internal edges: 148
- external edges: 161
- largest SCC: 1 (is_dag: true)
- entrypoints: 2 (main_guard=1, pyproject_script=1)

## Top Hotspots

| path | change_count | coupling |
| --- | --- | --- |
| `src/codexray/cli.py` | 6 | 19 |
| `src/codexray/graph/build.py` | 3 | 12 |
| `src/codexray/graph/types.py` | 1 | 19 |
| `src/codexray/graph/csharp_index.py` | 2 | 9 |
| `src/codexray/graph/resolve.py` | 3 | 5 |

## Recommendations

1. Top hotspot: `src/codexray/cli.py` (change=6, coupling=19). 책임 분리·테스트 추가 우선.
2. `documentation` grade F (score 5). detail: {'items_total': 397, 'documented': 21}
3. `cohesion` grade D (score 59). detail: {'groups_evaluated': 2}


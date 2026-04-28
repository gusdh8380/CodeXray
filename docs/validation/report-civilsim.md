<!-- codexray-report-v1 -->
# CodeXray Report — `/Users/jeonhyeono/Project/personal/CivilSim`
**Date:** 2026-04-28

## Overall Grade: D (40)

| dimension | grade | score | detail |
| --- | --- | --- | --- |
| coupling | F | 33 | avg_fan_inout=6.72, max=44 |
| cohesion | A | 92 | groups_evaluated=3 |
| documentation | F | 33 | documented=86, items_total=262 |
| test | F | 4 | ratio=0.02, src_loc=8684, test_loc=194 |

## Inventory

| language | file_count | loc | last_modified_at |
| --- | --- | --- | --- |
| C# | 53 | 8878 | 2026-03-05T17:55:20+09:00 |

## Structure

- nodes: 53
- internal edges: 178
- external edges: 121
- largest SCC: 14 (is_dag: false)
- entrypoints: 34 (unity_lifecycle=34)

## Top Hotspots

| path | change_count | coupling |
| --- | --- | --- |
| `Assets/Scripts/Core/GameManager.cs` | 15 | 45 |
| `Assets/Scripts/Core/GameEvents.cs` | 11 | 25 |
| `Assets/Scripts/UI/HUDController.cs` | 12 | 14 |
| `Assets/Scripts/Buildings/BuildingPlacer.cs` | 11 | 15 |
| `Assets/Scripts/UI/SettingsPanelUI.cs` | 14 | 11 |

## Recommendations

1. Top hotspot: `Assets/Scripts/Core/GameManager.cs` (change=15, coupling=45). 책임 분리·테스트 추가 우선.
2. `coupling` grade F (score 33). detail: {'avg_fan_inout': 6.72, 'max': 44}
3. `documentation` grade F (score 33). detail: {'items_total': 262, 'documented': 86}
4. `test` grade F (score 4). detail: {'src_loc': 8684, 'test_loc': 194, 'ratio': 0.02}
5. Cycle detected — largest SCC size 14, 39 SCCs total. 사이클 분해 검토.


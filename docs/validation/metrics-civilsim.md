# Metrics — CivilSim 검증

**Change:** `add-graph-metrics`
**Run date:** 2026-04-28 (KST)
**Target:** `/Users/jeonhyeono/Project/personal/CivilSim`

## Result

```
$ uv run codexray metrics /Users/jeonhyeono/Project/personal/CivilSim
{
  "schema_version": 1,
  "graph": {
    "node_count": 53,
    "edge_count_internal": 457,
    "edge_count_external": 121,
    "scc_count": 39,
    "largest_scc_size": 15,
    "is_dag": false
  }
}
```

| metric | value |
|---|---|
| nodes | 53 (C# only) |
| internal edges | 457 |
| external edges | 121 |
| SCCs | 39 |
| **largest SCC** | **15** |
| **is_dag** | **false** |

## Top fan_in (가장 많이 import되는 모듈)

| path | fan_in | fan_out | external |
|---|---|---|---|
| Assets/Scripts/Core/CityProgressionManager.cs | 24 | 6 | 1 |
| Assets/Scripts/Core/GameClock.cs | 24 | 0 | 1 |
| Assets/Scripts/Core/GameEventBus.cs | 24 | 0 | 3 |
| Assets/Scripts/Core/GameEvents.cs | 24 | 3 | 1 |
| Assets/Scripts/Core/GameHotkeySettings.cs | 24 | 0 | 4 |

## Performance

| metric | value |
|---|---|
| wall (`real`) | **0.49s** |
| user | 0.39s |
| sys  | 0.04s |
| budget | 5.00s |
| margin | ≈ 10× under budget |

## Observations

1. **largest_scc_size = 15** — 15개 파일이 서로 순환 의존하는 강연결요소가 존재한다. 이게 정량 평가(#2)에서 결합도 등급 하락 + 핫스팟(#4) 후보로 직결되는 신호.
2. **`Core` namespace 5개 파일 모두 fan_in 24** — 1:N 매핑 부산물 (한 `using CivilSim.Core;`가 5 파일 전부 가리킴). type-resolution 후속 변경(`add-graph-csharp-types`)에서 정확도 향상 시 이 수치가 분산됨.
3. **`is_dag = false`** — 사이클이 있다는 사실 자체가 가치 있는 발견. 사용자가 "어디 사이클이 있나" 본격 보고 싶을 때 후속 변경으로 `largest_scc_members` 노출.
4. **5초 게이트 압도적 통과** — 0.49s. 트리 노드 수가 53이라 알고리즘 부하는 무의미. 2자리수 노드 트리에서는 메트릭 비용 사실상 무료.

## Caveats

- C# `using` namespace 매칭의 보수성 때문에 `Core` 폴더 5개 파일이 모두 같은 fan_in을 갖는다. 실제 의존성 그래프와 차이는 후속 type-resolution 변경에서 좁혀진다.
- preprocessor (`#if UNITY_EDITOR`) 내부 `using`도 모두 추출됨 → 일부 거짓양성 가능.

## Next signals from this metric

- **결합도 등급 입력**: 가장 큰 SCC(15)의 멤버를 후속 변경에서 노출하면 사용자가 "어느 모듈 묶음을 풀어야 하는가" 직접 식별 가능
- **핫스팟 매트릭스의 한 축**: `fan_in × fan_out × external_fan_out` 조합으로 변경 위험도 추정 → MVP feature #4의 입력

# Dependency Graph — C# / CivilSim 검증

**Change:** `add-graph-csharp`
**Run date:** 2026-04-28 (KST)
**Target:** `/Users/jeonhyeono/Project/personal/CivilSim` (Unity, C# only)

## Result

```
$ time uv run codexray graph /Users/jeonhyeono/Project/personal/CivilSim
```

| metric | value |
|---|---|
| nodes | 53 (모두 `language: "C#"`) |
| internal edges | **457** |
| external edges | 121 (`UnityEngine`, `System.*` 등) |
| schema_version | 1 |

## Performance

| metric | value |
|---|---|
| wall (`real`) | **0.66s** |
| user | 0.37s |
| sys  | 0.07s |
| budget | 5.00s |
| margin | ≈ 7.6× under budget |

## Sample edges

```json
{"from": "Assets/Editor/PandazoleBuildingDataGenerator.cs", "to": "Assets/Scripts/Buildings/BuildingData.cs", "kind": "internal"}
{"from": "Assets/Editor/PandazoleBuildingDataGenerator.cs", "to": "Assets/Scripts/Buildings/BuildingDatabase.cs", "kind": "internal"}
{"from": "Assets/Editor/PandazoleBuildingDataGenerator.cs", "to": "Assets/Scripts/Buildings/BuildingPlacer.cs", "kind": "internal"}
```

→ 한 파일이 `using CivilSim.Buildings;` 한 줄로 같은 namespace 내 여러 파일에 internal 엣지를 만든다 (Decision 1의 1:N 모델 의도대로 동작).

## Walk filter sanity

- 51,063 → 53: Unity의 `Library/`, `obj/`, `Builds/`, `*.csproj`, `*.sln` 등이 `.gitignore`에 의해 정확히 배제. 1차 인벤토리 검증과 일관됨.

## Spot checks

- **UnityEngine**: `using UnityEngine;` → external (트리에 namespace `UnityEngine` 선언 파일 없음 — 외부 어셈블리)
- **CivilSim.Core**, **CivilSim.Buildings**: 트리 내 다수 파일이 선언 → internal 매핑 정상
- **글로벌 namespace 파일** (예: `BuildingTestInput.cs`): namespace 선언 없음 → 노드로는 등장하나 internal target이 될 수 없음 (intended)

## Environment

- macOS Darwin 25.4.0 (arm64)
- Python 3.14.3 / uv 0.11.7
- CodeXray 0.1.0 (C# 추가본)
- 의존성: 변동 없음

## Observations

1. **5초 게이트 통과** — 0.66s, JS/TS/Python(0.21s) 대비 약 3배지만 namespace 인덱스 빌드 + 1:N 매칭 추가 비용 감안 시 합리.
2. **internal/external 비율 79%/21%** — CivilSim이 자기 자신을 namespace 단위로 강하게 참조한다는 신호. 후속 핫스팟·결합도 분석에 유용한 입력.
3. **MVP의 첫 단추 게이트가 C#에도 적용됨** — 이제 사용자의 검증 자산에서 모든 1차 분석(인벤토리 + 그래프)이 의미 있는 결과를 낸다.
4. **1:N 모델의 보수성** — `using CivilSim.Buildings;` 한 줄이 Buildings namespace 모든 파일과 엣지를 만든다. type-resolution 후속 변경에서 정확도 향상 여지.

## Next

- `add-graph-java`: Java `import` 추출 (검증 자산 부재로 후순위)
- `add-graph-csharp-types`: C# type-resolution으로 1:N → 1:1 정확도 향상 (실제 사용된 type만 internal target)
- `add-graph-metrics`: fan-in/fan-out/SCC/중심성 — 같은 JSON 위에 정량 평가 1차 입력 마련
- `add-entrypoints`: `Program.cs`의 `Main`, MonoBehaviour 라이프사이클(`Awake`, `Start`, `Update`) 진입점 인식

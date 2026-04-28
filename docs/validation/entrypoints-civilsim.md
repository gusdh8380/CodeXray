# Entrypoints — CivilSim 검증

**Change:** `add-entrypoints`
**Run date:** 2026-04-28 (KST)
**Target:** `/Users/jeonhyeono/Project/personal/CivilSim`

## Result

| metric | value |
|---|---|
| count | 34 |
| `unity_lifecycle` | 34 |
| `main_method` | 0 |
| `pyproject_script` | 0 |
| `package_*` | 0 |

전부 Unity MonoBehaviour 라이프사이클 — Unity 게임은 `Main` 메서드 없이 Scene + MonoBehaviour 모델로 진입점이 분산된다는 사실이 결과로 드러남.

## Sample entries

```json
{ "path": "Assets/Scripts/Buildings/BuildingInstance.cs", "language": "C#", "kind": "unity_lifecycle", "detail": "Awake" },
{ "path": "Assets/Scripts/Buildings/BuildingManager.cs",  "language": "C#", "kind": "unity_lifecycle", "detail": "Awake, Start" },
{ "path": "Assets/Scripts/Buildings/BuildingPlacer.cs",   "language": "C#", "kind": "unity_lifecycle", "detail": "Awake, OnDestroy, Start, Update" },
{ "path": "Assets/Scripts/BulidingTestInput.cs",          "language": "C#", "kind": "unity_lifecycle", "detail": "Update" },
{ "path": "Assets/Scripts/Camera/RTSCameraController.cs", "language": "C#", "kind": "unity_lifecycle", "detail": "Awake, Update" }
```

## Performance

| metric | value |
|---|---|
| 1차 측정 (read 후 classify) | 3.89s — 5초 예산 위태 |
| 2차 측정 (classify 후 read로 수정) | **0.45s** |
| budget | 5.00s |
| margin (수정 후) | ≈ 11× under budget |

### 성능 회귀 발견 + 수정
1차 구현은 walk → read_text → classify 순서로, 비-소스 파일까지 모두 read해 1.4초 가량 낭비되고 있었다. classify 후 읽도록 순서를 바꿔 8.6× 속도 향상. 다른 명령(inventory, graph, metrics)은 처음부터 classify-first 패턴이라 이슈 없었음. 회귀 방지를 위해 향후 디텍터 추가 시 같은 순서를 유지할 것 (디자인 문서 기록 가치).

## Observations

1. **34개 라이프사이클 진입점** = Unity 게임의 실행 시작점이 흩어져 있음. 도달성 분석을 할 때 이들을 모두 root로 잡고 BFS/DFS 가능.
2. **detail 컬럼 활용도** — `BuildingPlacer.cs`가 `Awake, OnDestroy, Start, Update` 4개 → 활성/비활성/매 프레임 모두 관여하는 핵심 객체. 핫스팟 가중치 후보.
3. **Manifest 부재** — Unity 프로젝트라 pyproject/package.json 없음. 정상.
4. **MVP 구조 분석 단계 거의 완성** — inventory + graph + metrics + entrypoints 4축. 남은 1c "호출 관계"는 함수 단위 분석으로 후속.

## Environment

- macOS Darwin 25.4.0 (arm64)
- Python 3.14.3 / uv 0.11.7
- CodeXray 0.1.0 (entrypoints 추가본)

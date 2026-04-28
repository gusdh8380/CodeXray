# Dashboard — CivilSim 검증

**Change:** `add-dashboard`
**Run date:** 2026-04-28 (KST)
**Target:** `/Users/jeonhyeono/Project/personal/CivilSim`
**Output:** [`dashboard-civilsim.html`](./dashboard-civilsim.html)

## 빠른 확인

```
$ codexray dashboard /Users/jeonhyeono/Project/personal/CivilSim > civilsim.html && open civilsim.html
```

| metric | value |
|---|---|
| wall (`real`) | **2.40s** |
| HTML 크기 | ~81KB |
| 헤더 grade | **D (40)** |
| v1 marker | ✓ first 5 lines |
| D3 CDN script tags | 1 |
| inline JSON 블록 | 6 |
| 그래프 노드 | 53 (C# only) |
| internal 엣지 | 178 |

## 사용자가 직접 확인할 것

브라우저에서 `dashboard-civilsim.html`을 열어:
1. 헤더에 path, 날짜, **D (40)** 표시
2. Force-directed 그래프에 53 노드 — `Core` 폴더 노드들이 큼(coupling 큼) 빨강(hotspot)
3. 1순위 hotspot `Assets/Scripts/Core/GameManager.cs` 시각적으로 두드러짐 (가장 큰 빨간 노드 중 하나)
4. 검색 `Building` → Buildings/* 노드들만 강조, 나머지 흐려짐
5. 노드 클릭 → 패널에 `change_count`, `coupling`, `category=hotspot` 표시
6. `Assets/Scripts/BulidingTestInput.cs` 같은 진입점 노드는 `entrypoint` 필드에 `unity_lifecycle` 표시

## Observations

- CivilSim은 5초 예산의 절반 사용 (2.40s) — 그래프 빌드(0.55s) + metrics(0.49s) + hotspots(0.69s) + quality(0.95s) + entrypoints(0.45s) + inventory(0.52s) 누적
- HTML 80KB — 그래프 시각화에 충분히 작음
- 헤더 등급이 type-resolution 적용 후 측정한 D(40)와 일치 (회귀 없음)
- 모든 분석 데이터가 한 화면에서 — 사용자 첫 의사결정 자료로 1순위

## MVP feature #6 (인터랙티브 대시보드) 첫 사이클 통과
- Force-directed 그래프 ✓
- 검색 ✓
- 노드 클릭 → 파일별 상세 패널 ✓
- AI 정성 평가 통합은 후속 변경

# Hotspots — CivilSim 검증

**Change:** `add-hotspots`
**Run date:** 2026-04-28 (KST)
**Target:** `/Users/jeonhyeono/Project/personal/CivilSim`

## Result

| metric | value |
|---|---|
| change_count median | 3 |
| coupling median | 8 |
| hotspot | 23 |
| active_stable | 9 |
| neglected_complex | 7 |
| stable | 14 |

## Top hotspots (change × coupling)

| path | change | coupling |
|---|---|---|
| `Assets/Scripts/Core/GameManager.cs` | 15 | 45 |
| `Assets/Scripts/Core/GameEvents.cs` | 11 | 25 |
| `Assets/Scripts/UI/HUDController.cs` | 12 | 14 |
| `Assets/Scripts/Buildings/BuildingPlacer.cs` | 11 | 15 |
| `Assets/Scripts/UI/SettingsPanelUI.cs` | 14 | 11 |
| `Assets/Scripts/Economy/EconomyManager.cs` | 11 | 12 |
| `Assets/Scripts/Infrastructure/RoadBuilder.cs` | 8 | 12 |
| `Assets/Scripts/Grid/GridSystem.cs` | 6 | 15 |

## Performance

- wall: **0.69s** (5초 예산의 7배 마진)

## Observations

1. **`Core/GameManager.cs`가 압도적 1위** — 15 changes × 45 coupling. 게임 전체 중심 객체로, 자주 만지면서 의존성도 가장 큼. 이 파일을 어떻게 분해할지가 사용자의 가장 큰 의사결정 포인트.
2. **`Core/GameEvents.cs` 2위** — 11 changes × 25 coupling. 이벤트 버스 중심성 노출. 결합 분산 후보.
3. **23 hotspot / 53 노드 = 43%** — 일반적이지 않게 높은 비율. CivilSim이 활발히 개발 중인 게임이라 변경 빈도 분포가 두꺼운 꼬리. 임계치 median 적용으로 대다수가 high.
4. **type-resolution 적용 후 결과** — 이전 namespace 1:N 매핑 시대의 coupling 17.25 평균 대비 6.72로 현실에 가까워졌지만, 여전히 GameManager 같은 진짜 중심 객체는 45로 큰 신호 유지. 정확도 향상이 신호 약화로 이어지지 않음.

## 사용자 액션 가이드 (도구가 제시한 우선순위)

1. **`GameManager.cs`** — 가장 먼저. 책임 분리 검토.
2. **`GameEvents.cs`, `HUDController.cs`, `BuildingPlacer.cs`, `SettingsPanelUI.cs`, `EconomyManager.cs`** — 모두 11+ 변경 + 11+ 결합. 함께 핫스팟 군집.
3. neglected_complex 7개 — 안 건드리지만 결합 큼. 이해부터 시작 (테스트가 적은 영역일 가능성).

## MVP 핫스팟 매트릭스 첫 사이클 통과
- 변경 빈도(과거 행동) + 결합도(현재 영향) 두 축으로 4 카테고리 분류
- 사용자의 "어디부터?" 질문에 구체적 파일 5~8개를 우선순위로 제시
- 후속 변경(종합 리포트 + AI 정성 평가)이 같은 hotspot list를 입력으로 받아 권고를 자동 생성할 수 있음

# Hotspots — CodeXray 자기 검증

**Change:** `add-hotspots`
**Run date:** 2026-04-28 (KST)
**Target:** `/Users/jeonhyeono/Project/personal/CodeXray`

## Result

| metric | value |
|---|---|
| change_count median | 1 |
| coupling median | 4 |
| hotspot | 42 |
| active_stable | 24 |
| neglected_complex | 6 |
| stable | 2 |

## Top hotspots (change × coupling)

| path | change | coupling |
|---|---|---|
| `src/codexray/cli.py` | 5 | 17 |
| `src/codexray/graph/build.py` | 3 | 12 |
| `src/codexray/graph/csharp_index.py` | 2 | 9 |
| `src/codexray/graph/types.py` | 1 | 17 |
| `src/codexray/graph/resolve.py` | 3 | 5 |

## Performance

- wall: **0.22s** (5초 예산의 23배 마진)

## Observations

1. **`cli.py`가 1순위** — 모든 명령(inventory/graph/metrics/entrypoints/quality/hotspots) 추가 시 만져진 진입점. 변경 빈도와 결합도 모두 높음.
2. **`graph/types.py` (변경 1, 결합 17)** — `neglected_complex` 경계에 있지만 `>=` 클램프로 hotspot으로 분류. 실제로는 한 번 정의 후 안정. coupling 매우 높은 데이터클래스 모듈로 변경 위험은 큼 (인터페이스 깨지면 그래프 전체 영향).
3. **분포 비뚤어짐** — 30개 파일 중 42 hotspot? 합계 74. 동률 처리 때문 (median이 작은 트리에선 거의 모두 ≥). 작은 코드베이스에서 매트릭스 신호 약하다는 한계.
4. **MVP 핫스팟 매트릭스 첫 사이클 통과** — `git log` 통합 + 그래프 메트릭 결합 + 4 카테고리 분류 + 결정론적 출력.

## Caveats

- 작은 코드베이스(<50 파일)에서 median 임계치는 노이즈. 큰 트리에서 더 의미 있는 신호.
- "neglected_complex" 경계의 파일은 변경이 거의 없지만 영향 큼 — 후속 변경에서 별도 가중치 검토.

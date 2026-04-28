# Dashboard — CodeXray 자기 검증

**Change:** `add-dashboard`
**Run date:** 2026-04-28 (KST)
**Target:** `/Users/jeonhyeono/Project/personal/CodeXray`
**Output:** [`dashboard-self.html`](./dashboard-self.html)

## 빠른 확인

```
$ codexray dashboard . > dashboard.html && open dashboard.html
```

| metric | value |
|---|---|
| wall (`real`) | **0.95s** |
| HTML 크기 | ~96KB / 3,969 lines |
| 헤더 grade | D (57) |
| v1 marker | ✓ first 5 lines |
| D3 CDN script tags | 1 |
| inline JSON 블록 | 6 (inventory/graph/metrics/entrypoints/quality/hotspots) |

## 사용자가 직접 확인할 것

브라우저에서 `dashboard-self.html`을 열어:
1. 헤더에 codebase path, 날짜, **D (57)** 등급 표시 확인
2. Force-directed 그래프에 ~30 노드, internal 엣지 ~50개
3. 색상 분포 — 4 카테고리 색상이 보이는지
4. 검색 박스에 `cli`/`graph` 입력하면 매칭 노드만 강조
5. 노드 클릭 시 좌측 상세 패널에 path/coupling/change_count 표시

## Observations

- 5초 게이트 통과 (graph + metrics + hotspots + entrypoints + quality + inventory 다 빌드해도 1초 내)
- HTML self-contained — file:// 으로 열어도 동작 (D3만 CDN)
- 결정론 — `generated_date` 외에는 동일 입력 동일 출력 (test_deterministic_for_fixed_date 통과)

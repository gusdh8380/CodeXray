# Quality — CodeXray 자기 검증

**Change:** `add-quality-quant`
**Run date:** 2026-04-28 (KST)
**Target:** `/Users/jeonhyeono/Project/personal/CodeXray`

## Result

| dimension | score | grade | detail |
|---|---|---|---|
| **overall** | **58** | **D** | (4차원 평균) |
| coupling | 68 | C | avg fan_inout 3.17, max 14 |
| cohesion | 58 | D | 2 groups |
| documentation | 5 | F | 15 documented / 296 items |
| test | 100 | A | 1228 src LoC / 1119 test LoC (ratio 0.91) |

## Performance

| metric | value |
|---|---|
| wall (`real`) | **0.19s** |
| budget | 5.00s |
| margin | ≈ 26× under budget |

## Observations

1. **D 등급 — 정직한 자기 평가** — 도구가 자신을 평가했고 D를 받았다. 가장 큰 약점은 **documentation (5점)**: 296개 항목 중 15개만 docstring 보유.
2. **테스트 비율 우수 (A, ratio 0.91)** — TDD에 가깝게 짜온 결과 반영됨.
3. **응집도 D (58)** — `src/codexray`와 `tests` 두 그룹밖에 없는데, tests에서 src로 가는 엣지가 cross-group으로 잡혀 비율 떨어짐. 응집도 휴리스틱이 "테스트가 주된 의존인" 작은 코드베이스에서 약하다는 한계 노출. 후속 변경에서 tests 폴더 의존을 별도 가중하는 옵션 고려할 가치.
4. **결합도 C (68)** — 평균 fan_in+fan_out 3.17은 합리적. max 14는 `graph/types.py` 같은 중심 모듈.

## Action items (자기 도구가 제시한 다음 작업)

- documentation 점수 끌어올리기: 모듈 docstring + 함수 docstring 추가 → F → C/B 가능
- 응집도 휴리스틱 한계 인지 → 후속 변경에서 그룹 정의 정밀화

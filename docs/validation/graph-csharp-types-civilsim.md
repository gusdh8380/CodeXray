# C# Type-Resolution — CivilSim 비교 검증

**Change:** `add-graph-csharp-types`
**Run date:** 2026-04-28 (KST)
**Target:** `/Users/jeonhyeono/Project/personal/CivilSim`

## Before vs After

| metric | namespace 1:N (이전) | type-resolution (이번) | 변화 |
|---|---|---|---|
| nodes | 53 | 53 | 동일 |
| internal edges | 457 | **178** | **−61%** |
| external edges | 121 | 121 | 동일 |
| coupling avg | 17.25 | **6.72** | **−61%** |
| coupling max | 46 | **44** | -2 |

## Quality 변화 (CivilSim)

| dimension | 이전 | 이번 | 변화 |
|---|---|---|---|
| **overall** | **32 (F)** | **40 (D)** | **+8, F → D** |
| coupling | 0 (F) | 33 (F) | +33 |
| cohesion | 92 (A) | 92 (A) | 변화 없음 |
| documentation | 33 (F) | 33 (F) | 변화 없음 |
| test | 4 (F) | 4 (F) | 변화 없음 |

## Performance

| metric | value |
|---|---|
| graph wall | 0.55s |
| quality wall | 0.95s |
| budget | 5.00s |
| margin | ≈ 5× under budget |

## Observations

1. **internal 엣지 61% 감소** — `using CivilSim.Core;`만 적혀 있고 실제로 Core 안 type을 안 쓴 경우, 또는 Core 안 6개 type 중 2개만 쓴 경우 등 — 이전 1:N 매핑이 부풀린 의존성이 정확히 좁혀졌다.
2. **결합도 점수 0 → 33** — 평균 fan_in+fan_out 17.25 → 6.72. 등급은 여전히 F지만 D(40) 임계까지 7점 차. 더 정확한 type-resolution(상속·인터페이스·attribute 가중)을 후속에서 도입하면 D~C 가능성.
3. **overall F → D** — 등급이 한 단계 상승. CivilSim이 갑자기 좋아진 게 아니라 이전 측정이 노이즈 때문에 과도하게 낮았다는 신호.
4. **응집도·문서화·테스트 무영향** — 의도된 격리.
5. **5초 게이트 유지** — type 인덱스 + 사용 추출 추가에도 0.55s 그래프, 0.95s 품질.

## 1차 결정의 한계 (그대로 수용)

- partial class: 같은 (ns, type)이 여러 파일에 있으면 last-wins → 일부 internal 엣지가 한 파일에만 가는 부정확. 1차 수용.
- generic instance(`List<Building>`)에서 type 추출은 `Building`만 — 인스턴스 컨테이너(`List`)는 별도 typing 컨텍스트라 추출 안 함. 의도된 단순성.
- `var` 키워드 사용 시 RHS의 생성자 호출만 type 사용으로 잡힘 — 일반적 패턴 커버.

## Next signals

- 후속 가능: type-resolution v2 — 상속(`: Foo`), 인터페이스(`: IBar`), attribute(`[Baz]`) 컨텍스트별 가중치
- 후속 가능: alias `using A = X.Y` 처리, `global using` 처리
- CivilSim coupling을 D/C로 더 끌어올리려면 implicit own-namespace 외에 외부 라이브러리 type도 type 인덱스에서 정확히 분리 필요 (System.* 처리 정확도)

## MVP 정량 평가 정확도 1단계 향상 통과
- 같은 도구·같은 트리·다른 측정 결과 — 도구의 정확도 자체가 자기 검증 가능한 코드베이스 위에서 측정됐다는 것이 핵심.
- 후속 변경(핫스팟·AI 정성 평가)은 이 더 정확한 그래프 위에 쌓인다.

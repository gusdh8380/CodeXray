# Quality — CivilSim 검증

**Change:** `add-quality-quant`
**Run date:** 2026-04-28 (KST)
**Target:** `/Users/jeonhyeono/Project/personal/CivilSim`

## Result

| dimension | score | grade | detail |
|---|---|---|---|
| **overall** | **32** | **F** | (4차원 평균) |
| coupling | 0 | F | avg fan_inout **17.25**, max **46** |
| cohesion | 92 | A | 3 groups |
| documentation | 33 | F | 86 documented / 262 items |
| test | 4 | F | 8684 src LoC / 194 test LoC (ratio 0.02) |

## Performance

| metric | value |
|---|---|
| wall (`real`) | **1.10s** |
| budget | 5.00s |
| margin | ≈ 4.5× under budget |

## Observations

1. **결합도 0 (F)** — 가장 큰 약점. 평균 fan_in+fan_out 17.25, 최대 46. 이는 C# 1:N 매핑 부산물(`using CivilSim.Core;` 한 줄이 Core namespace 모든 파일에 엣지) 영향이 크다 — 후속 변경 `add-graph-csharp-types`에서 type-resolution 도입하면 분산되어 점수 개선 예상.
2. **응집도 A (92)** — Unity 표준 구조(`Assets/Scripts/Buildings`, `Assets/Scripts/Core`, `Assets/Scripts/Camera` 등)가 응집도 휴리스틱과 잘 맞음. 같은 폴더 내 의존이 대부분.
3. **문서화 F (33)** — 262 items 중 86개 documented. C# `///` XML doc 주석이 1/3에 있음. Unity 프로젝트로는 평균 이상이지만 절대 기준에서 F.
4. **테스트 F (4)** — Edit/PlayMode 합쳐 194 LoC. 8684 LoC 소스 대비 0.02 ratio. Unity 게임 일반적 패턴이지만 등급은 F.
5. **종합 F (32)** — 4차원 모두 약점이 있고 coupling/test가 특히 낮아 평균이 끌어내려졌다.

## Caveats

- **결합도 점수의 1:N 부산물**: C# 측정이 type 단위가 아닌 namespace 단위라 fan-out 부풀려짐. 사용자가 정확한 개선 영역을 알려면 `add-graph-csharp-types` 후 재측정 필요.
- 측정은 정량 신호일 뿐, 등급의 절대값보다 **차원별 약점 순위**(coupling > test > documentation > cohesion)와 자기/타 코드베이스 비교에 의미.

## Action items (도구가 제시한 다음 작업)

1. 결합도 — `Core` namespace 응집도 너무 큼. namespace를 더 세분화하거나 `Core`를 sub-namespace로 분할하면 1:N 매핑 영향 줄어듦
2. 테스트 — 0.02 ratio는 회귀 위험 큼. 핵심 매니저(GameClock, GameEventBus)부터 추가
3. 문서화 — `///` 주석을 public API 메서드부터

## MVP feature #2 (정량 평가) 첫 사이클 통과
- 4차원 산출 + A~F 매핑 + JSON 출력 + 결정론적 정렬
- CodeXray vs CivilSim 비교 가능 (D vs F, 차원별 강약점 명확)
- 후속 정량 변경(복잡도/중복도/보안) 동일 인터페이스 위에 추가 가능

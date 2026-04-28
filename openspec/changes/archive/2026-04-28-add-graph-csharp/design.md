## Context

`add-dependency-graph`로 Python·JS·TS의 파일↔파일 그래프가 잡혔다. C#은 가장 큰 검증 자산(CivilSim, Unity 50k 파일 트리)에 필요한 언어. C# 의존성 표현은 Python의 모듈 import와 다르다 — `using X.Y;`는 namespace를 끌어올 뿐이고, 그 namespace에 어떤 type이 있고 그 type이 어느 파일에 살고 있는지는 type-resolution 단계가 필요. 1차에서는 type-resolution을 우회하고 **namespace 단위 그래프**로 모델링한다 (1:N 엣지 허용). 충분히 의미있는 결합도/의존성 신호를 주면서, 1차 변경 분량을 작게 유지한다.

## Goals / Non-Goals

**Goals:**
- C# 파일을 그래프 노드로 등장시키고, `using X.Y;`를 internal/external 엣지로 분류
- CivilSim 5초 게이트 통과 + internal 엣지 N>0 확인
- 스키마 v1 그대로 (소비자 변경 없음)
- 기존 3개 언어 동작·테스트 0 회귀

**Non-Goals:**
- C# type-resolution (어떤 클래스가 어디 있는지) — type 단위 그래프는 후속 변경
- `using A = X.Y;` (alias) 추출 — 의미 보존 어려움, 1차 비대상
- `global using` 정확 처리 — 1차에서는 동일 정규식만 적용 (앞에 `global` 한정자만 추가됨, 매칭 안 됨)
- Java 추출 — 별도 변경 (Java 검증 자산 없음)
- C# preprocessor 디렉티브(`#if X`)로 분기되는 `using`의 조건부 평가 — 정적 텍스트로 모두 추출
- Roslyn 같은 외부 컴파일러 사용 — 1차 비대상

## Decisions

### Decision 1: 모델링 단위 — namespace ↔ 파일들
**선택 이유:**
- C# 파일은 1개 namespace에 속하지만(보통), 1개 namespace는 N개 파일에 분산된다
- `using X.Y;`는 그 namespace의 모든 type을 가시화 → 어느 type이 실제로 사용됐는지 모르면 "namespace 전체"가 가장 정확한 보수적 의존성 표현
- type-resolution을 1차에서 회피 → 변경 범위 작음

**결과:**
- 한 `using X.Y;`가 5개 파일의 namespace로 매핑되면 internal 엣지 5개 생성
- 노이즈 가능성: 한 type만 쓰지만 namespace 전체로 의존이 보임 → 의도한 보수성. 후속 변경에서 type-resolution 도입 시 정확도 향상.

### Decision 2: namespace 추출 — 정규식 2종
**대상 패턴:**
1. **블록 namespace**: `namespace X.Y` 다음 `{` 가 (개행 허용) — `\bnamespace\s+([A-Za-z_][A-Za-z0-9_.]*)\s*\{`
2. **파일 스코프 namespace** (C# 10+): `namespace X.Y;` — `\bnamespace\s+([A-Za-z_][A-Za-z0-9_.]*)\s*;`

**대안과 기각:**
- Roslyn 사용: 정확도 최고지만 .NET SDK 의존성 추가, 1차 비대상
- 한 정규식으로 통합: `\bnamespace\s+([A-Za-z_][A-Za-z0-9_.]*)\s*[{;]` — 가능하지만 가독성·유지보수에서 분리가 낫고 후속 변경에서 각각 다르게 처리할 가능성 있음

### Decision 3: `using` 추출 — 정규식 1종
- 패턴: `^\s*using(?:\s+static)?\s+([A-Za-z_][A-Za-z0-9_.]*)\s*;` (멀티라인 모드)
- alias (`using A = X.Y;`)는 `=` 때문에 매칭되지 않음 — 의도된 동작
- `global using X.Y;`는 `global` 때문에 매칭되지 않음 (1차) — Decision 4 참조
- 주석 안의 `using` 매칭은 거짓양성 가능 (Python/JS와 동일 한계, 수용)

### Decision 4: `global using` 처리 — 1차 비대상
**이유:** `global using`은 namespace를 솔루션 전체로 끌어올리는 어셈블리 수준 메커니즘. 정확히 처리하려면 `.csproj` 수준 처리가 필요. 1차에서는 비대상으로 두고, CivilSim 검증에서 `global using`이 핵심 의존성 신호인지 관찰. 핵심이라면 후속 변경.

### Decision 5: namespace 인덱스 위치 — `src/codexray/graph/csharp_index.py`
- 단일 함수 `build_namespace_index(cs_files: Iterable[Path]) -> dict[str, set[Path]]`
- `build.py`가 시작 시 1회 호출, 결과를 `resolve()`에 전달
- 인덱스에 빈 namespace(`""` 또는 미발견)는 키로 만들지 않음 → 글로벌 namespace 파일은 internal target이 될 수 없음 (사용자가 명시적으로 namespace 선언 안 한 파일은 의존성 그래프 가시성이 자연스럽게 떨어짐 — 의도된 동작)

### Decision 6: `resolve()` 시그니처 확장 — 마이그레이션
- 기존: `resolve(raw, root, internal_paths) -> Path | None`
- 신규: `resolve(raw, root, internal_paths, namespace_index) -> list[Path] | None`
- 반환 타입을 `Path | None`에서 `list[Path] | None`으로 변경 (1:N 매칭을 허용하기 위해)
- Python/JS 경로는 1:1이라 list 길이 ≤ 1
- C#만 list 길이 ≥ 1 가능
- `build.py`는 list를 받아 각 element에 internal 엣지 1개씩 만든다

**대안 기각:** 별도 `resolve_csharp` 함수만 두고 기존 시그니처 유지 → build.py 분기 코드가 늘고 일관성 깨짐

### Decision 7: 결정론 정렬 유지
- 1:N 엣지가 추가돼도 기존 정렬 (`from`, `to`, `kind`)에서 결정론 보장
- internal 엣지가 같은 `from`에서 N개 다른 `to`로 가도 `to` 사전순으로 정렬됨

### Decision 8: 1차 검증 게이트
- CivilSim 트리 (`/Users/jeonhyeono/Project/personal/CivilSim`)
- 통과 조건: ≤ 5초, internal 엣지 ≥ 1, 노드 ≥ 1
- 결과를 `docs/validation/graph-csharp-civilsim.md`에 캡처

## Risks / Trade-offs

- **[리스크] namespace 인덱스가 비어있는 트리** (모든 파일 글로벌 namespace 또는 namespace 미선언) → 모든 `using`이 external. 빈 그래프나 다름없음. **완화:** spec scenario에 명시 + 검증 메모에서 트리 특성을 기록
- **[리스크] 1:N 폭발** — 큰 namespace(예: `using UnityEngine;`)에 수백 파일이 매핑돼 엣지 수 폭증 → 그러나 UnityEngine은 외부 패키지라 트리에 없으므로 external. 사용자 정의 큰 namespace에서만 발생, 5초 예산 내라면 수용.
- **[리스크] alias 비처리** — `using G = System.Collections.Generic;` 같은 패턴이 흔함. 1차 무시, 후속 변경에서.
- **[리스크] preprocessor 분기** — `#if UNITY_EDITOR using ... #endif` 같은 조건부 `using`을 모두 추출. 거짓양성. 수용.
- **[트레이드오프] type 단위가 아닌 namespace 단위** — 결합도 측정 시 과대 추정 가능. 1차 의도된 보수성. 후속 변경에서 정확도 향상.

## Open Questions

- C# `Microsoft.Build.Locator`나 Roslyn 통합 시 외부 의존성 무게가 어디까지 허용되는가? (정확도 필요해질 때 결정)
- alias·global using·tsconfig paths를 한 변경에서 묶을지 분리할지 (지금은 분리 가정)

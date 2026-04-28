## Why

`add-graph-csharp`의 1:N 매핑이 결합도 점수를 부풀린다 (CivilSim coupling F=0, avg fan_inout 17.25). `using CivilSim.Core;` 한 줄이 Core 폴더 모든 .cs 파일로 internal 엣지를 만들어, 실제로는 1~2개 type만 쓰는데 5+ 파일과의 의존이 그래프에 등장한다. type 인덱스 + 파일별 type 사용 추출을 더해 use-driven 1:1로 좁히면 결합도/응집도/핫스팟 측정 모두 더 신뢰할 만한 신호를 낸다.

## What Changes

- `csharp_index.py`를 namespace 인덱스 + (namespace, type_name) 인덱스 두 개로 확장
- 모든 `.cs` 파일을 1회 스캔해 각 파일이 선언하는 type 추출 — `class X`, `interface I`, `struct S`, `record R`, `enum E` (한 namespace 블록 또는 file-scoped namespace 안의 type)
- 새 헬퍼: `extract_type_usages(source_code: str) -> set[str]` — 주석/문자열 제거 후 PascalCase 토큰(`\b[A-Z]\w*\b`) 모두 추출
- `resolve()` C# 분기 변경:
  - `using N;`이 namespace 인덱스에 없는 N → external (변동 없음)
  - `using N;`이 인덱스에 있는 N + 파일이 N에 속한 type 중 하나 이상을 토큰으로 사용 → 그 type 파일들로 internal 엣지 (use-driven, 자기 자신 제외)
  - `using N;`이 인덱스에 있지만 파일이 그 namespace의 어떤 type도 사용하지 않음 → **엣지 생성 안 함** (이전엔 1:N으로 모두 만들었음)
- 파일 자체의 declared namespace 안 type도 implicit하게 사용 가능 — 예: `BuildingManager.cs`가 `namespace CivilSim.Buildings`이고 `Building` type을 쓰면 같은 namespace의 `Building.cs`로 internal 엣지 (using 안 적어도)
- spec MODIFIED — `dependency-graph` capability의 "C# namespace 인덱스 해석"은 use-driven 1:1로 변경, "C# type 사용 추출" 신규 ADDED

## Capabilities

### New Capabilities
<!-- 해당 없음 -->

### Modified Capabilities
- `dependency-graph`: C# 해석 정확도 향상. namespace 단위 1:N → type 단위 1:1. 사용되지 않는 `using`은 엣지 생성 안 함.

## Impact

- 신규 코드: `csharp_index.py` 확장 (type extraction + namespace boundary parsing), `csharp_parser.py`에 `extract_type_usages` 추가, `resolve.py` C# 분기 재작성, `build.py` 인덱스 빌드 변경
- 신규 의존성 없음 — 정규식만
- 기존 동작 변경 — CivilSim에서 internal 엣지 수 감소 예상 (현재 457 → 사용량에 따라 감소, 종합 결합도 점수 상승)
- 검증 게이트: CivilSim에서 internal 엣지 ≥ 1, 5초 내, 결합도 점수 개선 확인
- 다른 명령(inventory/metrics/entrypoints/quality)은 그래프 결과를 받기만 하므로 자동 반영

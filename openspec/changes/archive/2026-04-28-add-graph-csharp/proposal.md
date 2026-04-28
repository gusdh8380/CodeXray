## Why

`add-dependency-graph`는 Python·JavaScript·TypeScript만 다뤘다. 사용자의 검증 자산(Unity 게임 `CivilSim`)은 C#이라 그래프 명령이 의미 있는 internal 엣지를 만들지 못한다. C# `using` 추출과 namespace ↔ 파일 인덱스 기반 internal 해석을 추가해, 첫 단추 검증 게이트(CivilSim 5초 내 의미있는 그래프)를 다시 활성화한다. Java는 별도 변경에서.

## What Changes

- 새 1차 대상 언어: **C#** (`.cs`) — Python·JS·TS와 같은 그래프에 합쳐진다 (스키마 v1 유지)
- 새 파서: `src/codexray/graph/csharp_parser.py`
  - `using X.Y;`, `using X.Y.Z;`, `using static X.Y.Type;` 추출
  - alias `using A = X.Y;`는 1차 비대상 (정규식이 매칭하지 않음)
  - `global using` (C# 10) 키워드는 1차 비대상
- 새 해석 모드: namespace 인덱스
  - 트리의 모든 `.cs` 파일을 1회 스캔, 각 파일이 선언한 namespace 집합 추출
  - 인덱스: `{namespace_name -> {files...}}`
  - `using X.Y;` → 인덱스 정확 일치 시 해당 namespace의 모든 파일로 internal 엣지 (1:N 가능)
  - 정확 일치 실패 시 external (raw 문자열 그대로)
- `src/codexray/graph/build.py` 수정: 대상 언어 set에 C# 추가, build 시작 시 namespace 인덱스 1회 빌드
- `src/codexray/graph/resolve.py` 시그니처 확장: `resolve(raw, root, internal_paths, namespace_index)` — Python·JS는 인덱스 무시
- 출력 스키마 v1 그대로 (호환 유지). `language: "C#"` 노드와 internal/external 엣지가 추가될 뿐
- `dependency-graph` capability spec MODIFIED: 1차 대상 언어를 4개로 갱신, 새 Requirement "C# using 추출"·"C# namespace 인덱스 해석" 추가

## Capabilities

### New Capabilities
<!-- 해당 없음 — 기존 capability 확장 -->

### Modified Capabilities
- `dependency-graph`: 1차 대상 언어를 Python/JS/TS/C# 4개로 확장. 워킹·언어 분류 재사용 Requirement의 대상 언어 정의를 갱신하고, C# 추출/해석 Requirement 2개를 추가.

## Impact

- 신규 코드: `src/codexray/graph/csharp_parser.py`, namespace 인덱스 빌더(이름 미정 — `resolve.py` 또는 새 `csharp_index.py`에 격리)
- 신규 의존성 없음 (정규식만)
- 기존 동작 변경: Java(`.java`) 파일은 여전히 비대상. C# 파일은 노드로 등장 (이전엔 미등장)
- 검증 게이트: CivilSim 5초 내 표시 + internal 엣지 N>0
- Spec 마이그레이션 필요 없음 (스키마 v1 호환)

## Why

인벤토리는 "무엇이 있는가"만 답한다. 다음 분석(품질 등급·핫스팟·진입점 식별)은 모두 "무엇이 무엇에 의존하는가"를 알아야 의미를 가진다. 가장 작은 의존성 추출(파일↔파일 import) 한 사이클을 먼저 만들면 후속 단계가 동일 그래프 위에 누적될 수 있다. AST 기반 결정론적 추출만 한 차례 다지고, 시각화·메트릭(중심성·모듈 결합도)은 후속 변경에 떠넘긴다.

## What Changes

- 새 CLI 진입점: `codexray graph <path>` (`codexray inventory`와 같은 워킹/무시 규칙 재사용)
- 출력: stdout으로 JSON 1개 — `{"nodes": [...], "edges": [...]}`
  - 노드: 분석 대상 소스 파일 1개당 1개 (`{"path": "...", "language": "..."}`)
  - 엣지: import/require 한 건당 1개 (`{"from": "<path>", "to": "<resolved-path-or-module-string>", "kind": "internal"|"external"}`)
- 1차 추출 언어: **Python · JavaScript · TypeScript** (3개)
  - Python: `ast` 모듈 — `import X`, `from X import Y`, `from .X import Y` (relative)
  - JS/TS: 정규식 — `import ... from "X"`, `import "X"`, `require("X")`, dynamic `import("X")`
- 모듈 → 파일 해석:
  - Python: 같은 패키지 내 `.py`로 매핑 시도, 실패 시 `kind: "external"`
  - JS/TS: 상대 경로(`./`, `../`) + 확장자 자동 추정(`.ts`, `.tsx`, `.js`, `.jsx`, `.mjs`, `.cjs`, `index.*`) 시도, 실패 시 `kind: "external"`
- `--format` 옵션은 추가하지 않는다 (JSON 단일 출력)

## Capabilities

### New Capabilities
- `dependency-graph`: 입력 디렉토리에서 같은 언어 내 import/require를 추출해 파일↔파일 / 파일↔외부모듈 그래프(JSON)를 만드는 능력. 후속 변경(품질 평가·핫스팟·진입점)이 이 그래프를 입력으로 사용한다.

### Modified Capabilities
- `inventory`: 변경 없음 — 워킹/언어 분류 모듈은 그대로 재사용한다 (요구사항 변경 아님, 코드 의존만)

## Impact

- 신규 코드: `src/codexray/graph/` 하위에 parser·resolver·CLI 통합
- 신규 의존성 없음 — Python `ast`(stdlib) + 정규식만 사용
- 기존 모듈 영향: 없음. `walk`, `language`, `loc`는 그대로
- 검증: 1차는 CodeXray 자기 자신(Python 단일 언어 자기참조 그래프)으로. JS/TS 검증은 작은 픽스처 트리(`tests/fixtures/`) + 통합 테스트로
- Java/C# 추출은 비-목표 → 후속 변경 `add-graph-jvm-clr`(가칭)에서 (CivilSim 검증은 그때부터 가능)

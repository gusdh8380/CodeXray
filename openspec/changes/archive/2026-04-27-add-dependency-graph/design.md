## Context

`add-inventory-cli`로 워킹·언어 분류·LoC 파이프라인이 잡혔다. 이번 변경은 그 위에 "import 추출 → 그래프 JSON 출력"의 한 사이클을 얹는다. 1차에서 Python + JS/TS만 다루는 것은 의도된 좁힘 — Java/C# 추출은 별도 변경에서, CivilSim 같은 C# 프로젝트의 풀 검증은 그때 시작.

## Goals / Non-Goals

**Goals:**
- 결정론적·AI 비의존 의존성 그래프(JSON)를 `codexray graph <path>`로 한 번에
- 후속 분석(중심성·핫스팟·진입점·품질 등급 가중치)이 같은 JSON을 입력으로 받을 수 있는 안정적 스키마 제공
- 같은 검증 게이트(5초/검증 코드베이스) 통과
- 기존 `walk`/`language`/`loc` 모듈에 변경 없음

**Non-Goals:**
- 시각화(DOT, HTML, force-directed) — 후속 UI 변경
- 호출 그래프(함수 단위) — 모듈/파일 단위만
- 동적 import 의미 분석(조건부 분기·런타임 변수) — 정적 텍스트만
- Java(`import com.x.Y`)·C#(`using X.Y`) 추출 — 별도 변경
- npm `package.json` 의존성 표기·`pip` 패키지 메타정보 — 외부 모듈은 raw 문자열로 두기만

## Decisions

### Decision 1: CLI 명령 — `codexray graph`
**선택 이유:** "graph" 한 단어로 의도 명확, 이후 `codexray graph --format dot` 같은 옵션 확장 가능.
**대안:** `deps` (의존성에 한정된 어휘. graph가 더 광범위), `imports` (의도가 의존성 전반인지 import 한정인지 모호)

### Decision 2: 출력 형식 — JSON 한 가지
1차에서는 stdout JSON만 지원. 사람이 읽을 표는 후속 변경에서 `--format table` 추가.
**JSON 스키마(고정):**
```json
{
  "schema_version": 1,
  "nodes": [
    {"path": "src/codexray/cli.py", "language": "Python"}
  ],
  "edges": [
    {"from": "src/codexray/cli.py", "to": "src/codexray/inventory.py", "kind": "internal"},
    {"from": "src/codexray/cli.py", "to": "typer", "kind": "external"}
  ]
}
```
- `path`/`from`/`to`(internal): 입력 루트 기준 상대경로, POSIX 슬래시
- `to`(external): 코드에 적힌 모듈 문자열 그대로 (`from .x import` 같은 비해석 상대 import는 internal 해석 시도, 실패 시 external)
- `schema_version`: 후속 변경에서 깨질 수 있다는 신호. 1로 시작.

**대안과 기각:**
- DOT 출력: 시각화 용도지만 사람이 읽기에 좋지 않고 후속 분석이 못 씀. JSON이 모든 후속 작업의 우선 입력.
- 표(rich.table): 노드/엣지 두 종류라 컬럼 정의가 어색. 후속 옵션으로 미룬다.

### Decision 3: Python 추출 — stdlib `ast`
- `ast.parse(source)` 후 `ast.walk`로 `ast.Import`, `ast.ImportFrom` 노드만 수집
- 문법 오류 파일은 빈 import 목록(노드는 추가, 엣지 0개)으로 처리하고 stderr에 1줄 경고
- `from .x import y` (level≥1) → 현재 파일의 패키지 상대경로로 환산해 internal 해석

**대안:** 정규식. 빠르지만 멀티라인·괄호 import·문자열 안의 `import` 키워드에서 거짓양성. AST가 정답.

### Decision 4: JS/TS 추출 — 정규식 (1차)
**대상 패턴:**
- `import ... from "X"` / `import "X"` / `import * as N from "X"` / `import { a, b } from "X"`
- `import("X")` (dynamic, 정적 문자열 인수만)
- `require("X")` (정적 문자열 인수만)

**정규식 구성:** 한 패턴으로 통합하지 말고 3개 분리(`from "X"`, `require("X")`, `import("X")`). 각 패턴은 큰따옴표/작은따옴표/백틱 모두 허용.

**한계 (수용):**
- 주석 안의 import 문자열 → 거짓양성. 첫 단추 수용. 후속 변경에서 ts AST(`@typescript-eslint/parser` 같은 외부 도구) 도입 검토.
- 동적 변수 import (`import(libName)`) → 추출 불가, 의도된 동작.

**대안 기각 — Tree-sitter:** 정확도 좋지만 1차 변경에 외부 네이티브 의존성 추가는 과함. JS/TS는 정규식, 1차 통과 후 정확도 부족이 드러나면 그때 도입.

### Decision 5: 모듈 → 파일 해석기
- `src/codexray/graph/resolve.py` 한 모듈에 격리
- 입력: `(source_file: Path, raw_module: str, language: str)` → `Path | None` (None이면 external)
- **Python 해석 규칙:**
  1. 절대 import (`import a.b.c`): 입력 루트(또는 `src/`) 기준으로 `a/b/c.py` 또는 `a/b/c/__init__.py` 시도
  2. 상대 import (`from .x import y`, level 1~N): `source_file`의 부모 디렉토리에서 N단계 위로 → 거기서 `x.py` 또는 `x/__init__.py`
- **JS/TS 해석 규칙:**
  1. 상대 경로(`./x`, `../x`): `source_file` 기준 `x` + 확장자 후보(`.ts`, `.tsx`, `.js`, `.jsx`, `.mjs`, `.cjs`, `/index.ts`, `/index.tsx`, ...) 순서로 stat
  2. 절대 경로(`/...`)·alias(`@/...`)·bare specifier(`react`): 1차에서는 모두 external (tsconfig paths 분석은 후속)
- **공통:** 해석 후 경로가 walk 결과에 포함된 파일이 아니면 `external`로 강등 (인벤토리 ignore 규칙과 일치 보장)

### Decision 6: 출력 안정성 — 정렬
- `nodes`: `path` 사전순 오름차순
- `edges`: `from` 사전순, 같으면 `to`, 같으면 `kind`
- 이유: diff 가능한 결정론적 출력. 후속 회귀 테스트에 필수.

### Decision 7: 패키지 구조 — `src/codexray/graph/` 서브패키지
- `graph/__init__.py` — 공개 API: `build_graph(root) -> Graph`
- `graph/python_parser.py` — `extract_imports(source: str) -> list[RawImport]`
- `graph/js_parser.py` — JS/TS 정규식 기반
- `graph/resolve.py` — 모듈 → 파일
- `graph/build.py` — walk + classify + parse + resolve → Graph
- `graph/serialize.py` — Graph → JSON (스키마 v1)

이렇게 분리하면 후속 변경에서 Java/C# 파서를 추가할 때 `graph/java_parser.py` 한 파일만 더 붙으면 끝.

### Decision 8: 성능 — 단일 패스, 직렬
- 인벤토리 5초 예산 안에서 추가로 1.5초 정도 더(파일 한 번 읽기 + 정규식/AST 1회). 멀티프로세싱 도입 보류.
- 5초 예산은 **전체 graph 명령 실행** 기준 (인벤토리와 별개 호출이므로 인벤토리 시간 제외)

## Risks / Trade-offs

- **[리스크] 정규식 JS/TS 파서 거짓양성** (주석 내 import) → 후속 변경 트리거 (정확도 게이트 추가 시). 1차에선 의도적 단순화 명시.
- **[리스크] 상대 import 해석 누락** (Python의 `__init__.py` 부재 패키지, JS의 `package.json` `exports`) → 1차에서는 unresolved → external. spec 시나리오로 명시.
- **[리스크] 검증 코드베이스가 좁음** (CodeXray 자기 자신은 작은 Python 트리) → 검증 메모는 "Python 자기참조 + 통합 테스트의 JS/TS 픽스처"로 충분하다고 명시. CivilSim(C#) 검증은 다음 변경에서.
- **[트레이드오프] JSON-only 출력** → 즉시 사람이 읽기 어려움. `jq`/`fx` 같은 도구로 보면 된다. 표 출력은 후속.
- **[리스크] 큰 파일에서 AST 파싱 시간 폭증** → Python AST는 수만 라인까지 ms 단위. 자동 생성 파일(`*.gen.py`)은 1차 범위 외. 5초 예산 내라면 수용.

## Open Questions

- 향후 `schema_version: 2`로 갈 트리거는 무엇인가? (Java 추가, 함수 단위 그래프, edge attribute 추가 — 확정 시 별도 ADR/변경에서 결정)
- alias 해석(`@/components`)은 별도 변경에서 `tsconfig.json paths`를 입력으로 받는 형태로 처리 — 인터페이스만 미리 생각해 둘 것

## Context

이미 워킹·언어 분류·그래프·메트릭이 잡혔다. 이번 변경은 트리에서 "진입점"을 한 번 훑어 정적으로 식별해 JSON으로 내놓는 단일 명령. 도달성/죽은 코드/핫스팟은 후속 변경에서 이 JSON을 입력으로 받는다.

## Goals / Non-Goals

**Goals:**
- 정적 결정론적 진입점 식별 (AI·런타임 분석 없음)
- Python·JS/TS·C# 1차 5개 언어 + Unity 특수 케이스 + 패키지 매니페스트 커버
- 5초 예산 안에 결과
- `entrypoints` JSON 스키마 v1 — 후속 변경의 입력 안정성

**Non-Goals:**
- 도달성·도달 불가 모듈 식별 — 후속
- 호출 그래프(함수 단위) — 후속
- 동적 진입점 (런타임 reflection, plugin loaders) — 비결정적
- IDE-specific 진입점 (`.csproj`의 `<StartupObject>`, `tsconfig`의 paths 기반) — 후속
- pytest/JUnit 같은 테스트 진입점 — 1차 비대상 (테스트는 별도 신호)

## Decisions

### Decision 1: 별도 명령 (`entrypoints`) vs 기존 명령 확장
**선택:** 별도 명령. 그래프·메트릭과 같은 패턴.
**이유:** 출력 스키마와 소비자가 다르다. 별도 capability로 격리하면 후속 변경에서 도달성 분석이 metrics + entrypoints 두 입력을 합치는 구조가 자연스럽다.

### Decision 2: Python `__main__` 가드 — AST 정확 매칭
- `ast.parse` 후 모듈 레벨 `If` 노드 순회
- 패턴: `If(test=Compare(left=Name(id="__name__"), ops=[Eq()], comparators=[Constant(value="__main__")]))`
- `__name__ == "__main__"` 와 `"__main__" == __name__` 둘 다 인식할지? **비대칭만 인식** (`__name__`이 left). 양방향 인식은 후속 변경. 명세에 명시.
- 이유: 정규식 대비 거짓양성 0, 후속 변경에서 패턴 확장 쉬움

### Decision 3: pyproject.toml — `tomllib` (Python 3.11+ stdlib)
- 트리 루트의 `pyproject.toml`만 읽음 (서브트리 1차 비대상)
- `[project.scripts]` dict의 각 키를 entry name으로
- `[project.gui-scripts]`도 같이 (optional, 1차에서 추가)
- 파싱 실패 → stderr 1줄 + skip

### Decision 4: package.json — `json` stdlib
- 트리 루트의 `package.json`만 (workspaces 1차 비대상)
- `bin`: string이면 단일 entry, dict이면 키별 entry, kind=`package_bin`
- `main`: 단일 string, kind=`package_main`
- `scripts`: dict, 각 스크립트 이름 키, kind=`package_script`
- 파싱 실패 → stderr 1줄 + skip

### Decision 5: C# `Main` 메서드 — 정규식
- 패턴: `(?:public|private|internal|protected)?\s*static\s+(?:async\s+)?(void|int|Task(?:<\s*int\s*>)?)\s+Main\s*\(`
- `unsafe`/`partial`/`extern` 같은 한정자는 1차 비대상 (드물고, 만약 매칭 실패하면 false negative)
- 매칭 시 detail은 반환 타입 (`void`/`int`/`Task`/`Task<int>`)

### Decision 6: Unity MonoBehaviour 라이프사이클 — 정규식 2단계
1. **클래스 시그니처 매칭**: `class\s+\w+\s*:\s*MonoBehaviour` (또는 `:` 뒤 콤마 구분 첫 번째 또는 임의 위치, 다중 상속 X — 단일 base만 보지만 C#은 단일 상속 + 인터페이스라 base가 첫 번째 위치). 실용 정규식: `class\s+\w+\s*:\s*[^{]*\bMonoBehaviour\b`
2. **라이프사이클 메서드 매칭**: 클래스가 매칭된 파일에 한해, 메서드 정규식 — `\b(Awake|OnEnable|Start|FixedUpdate|Update|LateUpdate|OnDisable|OnDestroy)\s*\(`
3. 매칭된 메서드들을 콤마 join → detail
4. 한 파일 1 entry (kind=`unity_lifecycle`)

**대안 기각:** Roslyn/AST. 1차 변경에 비용 과대.

### Decision 7: 출력 형식 — JSON, 결정론적 정렬
- `entrypoints` 배열 — `path` 사전순, 같으면 `kind` 사전순
- 매니페스트 entry는 `path: "pyproject.toml"` 또는 `path: "package.json"` (트리 루트의 그 파일을 가리킴)
- 매니페스트 항목의 `language`는 `null` (JSON null) — 매니페스트는 언어 분류 대상 아님

### Decision 8: 패키지 구조 — `src/codexray/entrypoints/`
- `entrypoints/types.py` — `Entrypoint`, `EntrypointResult`
- `entrypoints/python_detector.py`, `csharp_detector.py`, `unity_detector.py`, `manifest_detector.py`
- `entrypoints/build.py` — 모든 디텍터 합산
- `entrypoints/serialize.py`
- `entrypoints/__init__.py`

### Decision 9: walk 통합
- `walk(root)` 한 번 호출, 결과를 분류해 디텍터에 분배
- 매니페스트 디텍터는 walk 결과 안에서 `pyproject.toml`/`package.json`을 찾음 (트리 루트 한정)

## Risks / Trade-offs

- **[리스크] Unity 정규식 거짓양성** — 주석 안의 `class X : MonoBehaviour` 매칭. 빈도 낮음. 수용.
- **[리스크] C# `Main` 한정자 가짓수 초과** → false negative 가능. 1차에서는 표준 시그니처(`static void Main`, `static async Task Main` 등) 우선.
- **[리스크] pyproject 파싱 실패가 트리에 없는 정상 경우** — 단순 skip, 결과 비어 보일 뿐. 정상 동작.
- **[트레이드오프] 한 파일에서 매칭된 진입점 종류가 여러 개** (예: C# Main + Unity 라이프사이클 둘 다) → 같은 path로 두 entry 만든다. dedupe 안 함. 명세에 명시.

## Open Questions

- pytest의 `if __name__ == "__main__": pytest.main()` 같은 테스트 러너 가드가 진입점인가? — 1차에서는 `main_guard`로 인식 (의도적 단순성). 도달성 분석 후속 변경에서 테스트/프로덕션 분리 결정.
- Unity ScriptableObject·EditorWindow도 진입점 카테고리에 추가할지? — 1차 비대상.

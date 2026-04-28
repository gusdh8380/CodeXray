## 1. C# 파서

- [x] 1.1 `src/codexray/graph/csharp_parser.py` — `extract_imports(source_code: str, source_path: Path) -> list[RawImport]`
- [x] 1.2 정규식: `^\s*using(?:\s+static)?\s+([A-Za-z_][A-Za-z0-9_.]*)\s*;` (멀티라인 모드)
- [x] 1.3 alias `using A = X.Y;` 미매칭 동작 검증 (정규식이 `=`를 허용하지 않음)
- [x] 1.4 `global using` 미매칭 동작 검증 (라인 시작에서 `using`만 허용, `global` 키워드 앞 X)
- [x] 1.5 단위 테스트 — 단순 using / using static / 멀티라인 / alias 미추출 / global 미추출 / 따옴표 비포함 (C#은 따옴표 X)

## 2. namespace 인덱스

- [x] 2.1 `src/codexray/graph/csharp_index.py` — `build_namespace_index(cs_files: Iterable[tuple[Path, str]]) -> dict[str, set[Path]]`
- [x] 2.2 블록 namespace 정규식: `\bnamespace\s+([A-Za-z_][A-Za-z0-9_.]*)\s*\{`
- [x] 2.3 파일 스코프 namespace 정규식: `\bnamespace\s+([A-Za-z_][A-Za-z0-9_.]*)\s*;`
- [x] 2.4 한 파일이 여러 namespace 블록을 가질 수 있음 (인덱스에 모두 추가)
- [x] 2.5 단위 테스트 — 단일 블록 / 다중 블록 / 파일 스코프 / namespace 미선언 (인덱스 미등재) / 동일 namespace 다중 파일

## 3. 해석기 확장

- [x] 3.1 `resolve()` 시그니처를 `(raw, root, internal_paths, namespace_index) -> list[Path]` 로 확장 (반환 타입이 list로 통일)
- [x] 3.2 Python/JS 경로는 list 길이 ≤ 1 (기존 동작 유지)
- [x] 3.3 C#: `raw.raw`가 `namespace_index`의 키와 정확 일치하면 그 set의 모든 파일을 list로 반환, 아니면 빈 list
- [x] 3.4 단위 테스트 — C# namespace 정확 일치 1:1 / 1:N / 인덱스 미등재 (빈 list) / Python·JS 회귀 (기존 1:1 동작 유지)

## 4. build.py 통합

- [x] 4.1 `_TARGET_LANGUAGES`에 `"C#"` 추가
- [x] 4.2 build 시작 시 C# 파일 모두 모아 `build_namespace_index` 1회 호출
- [x] 4.3 파서 디스패치에 C# 분기 추가
- [x] 4.4 `resolve()` 호출 부분을 list 반환에 맞게 갱신 — 빈 list면 external 엣지 1개, 비어있지 않으면 각 element에 internal 엣지 1개
- [x] 4.5 결정론 정렬 회귀 테스트 (기존 동일 동작)

## 5. 테스트

- [x] 5.1 통합 테스트 `tests/test_graph_csharp.py` — 단일 namespace 1:1 / 다중 namespace 1:N / 글로벌 namespace 미매칭 / using static / alias 무시
- [x] 5.2 회귀 테스트 — 기존 Python·JS·TS 통합 테스트 모두 통과 (`test_java_excluded_other_targets_included`로 갱신)
- [x] 5.3 결정론 회귀 테스트 — 같은 입력 stdout 바이트 일치 (`test_deterministic_output` 통과)

## 6. 검증

- [x] 6.1 CodeXray 자기 자신 회귀 — `codexray graph .` 결과 30 nodes / 37 internal / 66 external (C# 신규 모듈 추가만큼 자연 증가, 기존 동작 유지)
- [x] 6.2 CivilSim 실측 — 0.66s, 53 nodes / 457 internal / 121 external. `docs/validation/graph-csharp-civilsim.md`에 캡처
- [x] 6.3 `openspec validate add-graph-csharp` 통과 재확인
- [x] 6.4 `ruff check` + `pytest` 모두 통과 (68/68)

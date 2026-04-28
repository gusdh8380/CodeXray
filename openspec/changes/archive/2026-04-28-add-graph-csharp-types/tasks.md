## 1. type 사용 추출

- [x] 1.1 `csharp_parser.py`에 `extract_type_usages(source_code: str) -> set[str]` 추가
- [x] 1.2 문자열·주석 제거 정규식 1회 적용 후 `\b[A-Z]\w*\b` 매칭
- [x] 1.3 단위 테스트 — 기본 매칭 / 문자열 안 토큰 무시 / 주석 안 토큰 무시 / 다중 사용 dedupe / 빈 파일

## 2. namespace 경계 + type 인덱스

- [x] 2.1 `csharp_index.py`를 확장: `build_indexes(cs_files) -> CSharpIndexes` (namespace_to_files, type_to_file, file_to_namespaces)
- [x] 2.2 namespace 블록 경계 — `{` `}` brace 카운터로 추적
- [x] 2.3 file-scoped namespace — `namespace X;` 이후 파일 끝까지가 X 범위
- [x] 2.4 type 정규식: `class|interface|struct|record|enum` 한정자 허용 + 이름 캡처
- [x] 2.5 단위 테스트 — 단일 namespace + class / 다중 namespace / 파일 스코프 namespace + class / 글로벌 namespace 미등록 / partial class last-wins

## 3. resolve 변경

- [x] 3.1 `resolve.py`를 분해: `resolve_python`, `resolve_js`, `resolve_csharp_types` (각각 list[Path] 반환)
- [x] 3.2 `resolve()`는 backward-compatible wrapper로 유지 (테스트 호환)
- [x] 3.3 `resolve_csharp_types(namespace, source, type_usages, type_index)` — `(namespace, type)`이 인덱스에 있고 자기 파일 아닌 것만 반환
- [x] 3.4 단위 테스트 — namespace + type 매칭 1:1 / 부분 사용 / 미사용 / 인덱스에 없는 namespace

## 4. build.py 통합

- [x] 4.1 `build_indexes`로 두 인덱스 + own-namespaces 빌드
- [x] 4.2 각 C# 파일에 대해 `extract_type_usages` 1회 호출
- [x] 4.3 explicit `using` 처리: namespace_index에 없으면 external, 있으면 type-driven internal (없으면 0 엣지)
- [x] 4.4 implicit own-namespace 처리: 자기 namespace 안 type을 사용하면 internal 엣지
- [x] 4.5 결정론 정렬 유지

## 5. 회귀 + 통합 테스트

- [x] 5.1 `test_graph_csharp.py` 갱신 — type 사용 시나리오 9개 (1:1, 1:N use-driven, unused 0 엣지, file-scoped, implicit own-namespace, 등)
- [x] 5.2 신규 `test_graph_csharp_types.py` — extract_type_usages + build_indexes 단위 테스트
- [x] 5.3 기존 Python·JS·TS 회귀 통과
- [x] 5.4 결정론 회귀

## 6. 검증

- [x] 6.1 CodeXray 자기 회귀 — C# 0개라 변동 없음 확인 (`pytest` 통과 = 회귀 없음)
- [x] 6.2 CivilSim 실측 — internal 엣지 **457 → 178 (61% 감소)**, coupling 0 → 33, **overall F → D**. `docs/validation/graph-csharp-types-civilsim.md`에 캡처
- [x] 6.3 5초 예산 유지 (graph 0.55s, quality 0.95s)
- [x] 6.4 `openspec validate add-graph-csharp-types` 통과
- [x] 6.5 `ruff check` + `pytest` 모두 통과 (163/163)

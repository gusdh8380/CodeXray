## 1. 패키지 스캐폴드

- [x] 1.1 `src/codexray/entrypoints/__init__.py` — `build_entrypoints`, `to_json`, 데이터클래스 노출
- [x] 1.2 `src/codexray/entrypoints/types.py` — `Entrypoint(path, language, kind, detail)`, `EntrypointResult(schema_version, entrypoints)` (frozen, slots)

## 2. Python 디텍터

- [x] 2.1 `entrypoints/python_detector.py` — `detect_main_guard(source_code: str) -> bool`
- [x] 2.2 AST 기반: 모듈 레벨 `If(test=Compare(left=Name("__name__"), ops=[Eq], comparators=[Constant("__main__")]))` 매칭
- [x] 2.3 SyntaxError 무시 (False 반환), 호출 측에서 예외 안 뜸
- [x] 2.4 단위 테스트 — 표준 가드 / 함수 내부 가드 미매칭 / 비대칭 비교 미매칭 / SyntaxError

## 3. C# 디텍터 (Main + Unity)

- [x] 3.1 `entrypoints/csharp_detector.py` — `detect_main_method(source: str) -> str | None` (반환 타입 detail)
- [x] 3.2 정규식 — `(?:public|private|internal|protected)?\s*static\s+(?:async\s+)?(void|int|Task(?:<\s*int\s*>)?)\s+Main\s*\(`
- [x] 3.3 `entrypoints/unity_detector.py` — `detect_unity_lifecycle(source: str) -> list[str]` (매칭된 메서드명 정렬)
- [x] 3.4 클래스 정규식 1: `class\s+\w+\s*:\s*[^{]*\bMonoBehaviour\b`
- [x] 3.5 메서드 정규식 2: `\b(Awake|OnEnable|Start|FixedUpdate|Update|LateUpdate|OnDisable|OnDestroy)\s*\(`
- [x] 3.6 단위 테스트 — Main void/int/async Task/async Task<int> / Unity MonoBehaviour + Update / 다중 라이프사이클 dedupe / MonoBehaviour 미상속 미매칭

## 4. 매니페스트 디텍터

- [x] 4.1 `entrypoints/manifest_detector.py` — `detect_pyproject(root: Path) -> list[Entrypoint]` (`tomllib` 기반)
- [x] 4.2 `[project.scripts]` 모든 키 → `Entrypoint(path="pyproject.toml", language=None, kind="pyproject_script", detail=key)`
- [x] 4.3 `detect_package_json(root: Path) -> list[Entrypoint]`
- [x] 4.4 `bin`: string → 1 entry, dict → 키별 entry, kind=`package_bin`
- [x] 4.5 `main`: string → 1 entry, kind=`package_main`
- [x] 4.6 `scripts`: dict 키별 entry, kind=`package_script`
- [x] 4.7 파싱 실패 → stderr 1줄 + 빈 list
- [x] 4.8 단위 테스트 — pyproject scripts / package.json bin 단일/객체 / main / scripts / 매니페스트 부재 / 잘못된 JSON·TOML

## 5. 빌더 + 직렬화

- [x] 5.1 `entrypoints/build.py` — `build_entrypoints(root: Path) -> EntrypointResult`
- [x] 5.2 walk 1회 + 매니페스트 1회: classify 후 읽기 (성능 회귀 방지)
- [x] 5.3 결정론 정렬: path ASC, kind ASC, detail ASC
- [x] 5.4 `entrypoints/serialize.py` — `to_json(result: EntrypointResult) -> str`

## 6. CLI 통합

- [x] 6.1 `cli.py`에 `entrypoints` 서브커맨드 추가
- [x] 6.2 경로 검증은 `_validate_dir` 재사용
- [x] 6.3 정상 흐름 — `build_entrypoints` → `to_json` → `print`
- [x] 6.4 단위 테스트 — JSON 파싱 가능성, 키 일관성

## 7. 검증

- [x] 7.1 통합 테스트 — Python 가드 / pyproject scripts / package.json bin/main/scripts / C# Main / Unity 라이프사이클 합쳐진 픽스처
- [x] 7.2 결정론 회귀 — 같은 트리 두 번 실행 stdout 바이트 일치
- [x] 7.3 CodeXray 자기 자신 실측 — 2 entrypoints, 0.20s. `docs/validation/entrypoints-self.md`
- [x] 7.4 CivilSim 실측 — 34 unity_lifecycle, 0.45s (성능 회귀 발견 + 수정 후). `docs/validation/entrypoints-civilsim.md`
- [x] 7.5 `openspec validate add-entrypoints` 통과
- [x] 7.6 `ruff check` + `pytest` 모두 통과 (118/118)

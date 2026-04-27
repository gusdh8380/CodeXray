## 1. 패키지 스캐폴드

- [x] 1.1 `src/codexray/graph/__init__.py` 생성 — 공개 API 시그니처(`build_graph`, `Graph`, `Node`, `Edge`) 노출
- [x] 1.2 `src/codexray/graph/types.py` — `Node`, `Edge`, `Graph` 데이터클래스 정의 (frozen, slots)
- [x] 1.3 `RawImport` 데이터클래스 정의 — `(source: Path, raw: str, level: int, kind_hint: Literal["py-abs","py-rel","js-rel","js-bare"])`

## 2. Python 파서

- [x] 2.1 `src/codexray/graph/python_parser.py` — `extract_imports(source_code: str, source_path: Path) -> list[RawImport]`
- [x] 2.2 `ast.parse` 사용 + `ast.walk`로 `Import`/`ImportFrom` 노드 수집
- [x] 2.3 `ast.Import`의 `names`는 절대 import (level=0)으로 처리, 별칭은 무시
- [x] 2.4 `ast.ImportFrom`의 `level >= 1`은 상대 import로, `level == 0`은 절대 import로 처리
- [x] 2.5 SyntaxError catch — 빈 리스트 반환 + stderr 경고 호출(상위 layer로 시그널)
- [x] 2.6 단위 테스트 — 절대 / from-relative / multi-name from / 별칭 / SyntaxError

## 3. JS/TS 파서

- [x] 3.1 `src/codexray/graph/js_parser.py` — `extract_imports(source_code: str, source_path: Path) -> list[RawImport]`
- [x] 3.2 정규식 3종 — `from "X"`, `require("X")`, `import("X")` (각 따옴표 3종 허용)
- [x] 3.3 dynamic import 변수 인수는 매칭하지 않음 (정규식이 정적 문자열만 캡처)
- [x] 3.4 단위 테스트 — ES import / import "side-effect" / require / dynamic import 정적/변수 / 따옴표 종류

## 4. 해석기 (모듈 → 파일)

- [x] 4.1 `src/codexray/graph/resolve.py` — `resolve(raw: RawImport, root: Path, internal_paths: set[Path]) -> Path | None`
- [x] 4.2 Python 절대 import — 후보 위치 순서: `<root>/<a>/<b>/<c>.py`, `<root>/<a>/<b>/<c>/__init__.py`, `<root>/src/<a>/<b>/<c>.py`, `<root>/src/<a>/<b>/<c>/__init__.py`
- [x] 4.3 Python 상대 import — `source_path.parent`에서 `level` 단계 위로, 거기서 `<module>.py` 또는 `<module>/__init__.py`
- [x] 4.4 JS/TS 상대 경로 — `source_path.parent / raw` 기준, 확장자 없으면 `.ts/.tsx/.js/.jsx/.mjs/.cjs` 순으로 stat, 디렉토리면 `index.*` 후보
- [x] 4.5 JS/TS 절대 경로·alias·bare specifier — 모두 None (external)
- [x] 4.6 해석된 경로가 `internal_paths`에 없으면 None (무시 디렉토리·비대상 언어 강등)
- [x] 4.7 단위 테스트 — Python abs / Python rel / JS ext-omit / JS index dir / JS bare / 무시 디렉토리 강등

## 5. 그래프 빌더 + 직렬화

- [x] 5.1 `src/codexray/graph/build.py` — `build_graph(root: Path) -> Graph`
- [x] 5.2 walk → classify → 1차 대상 언어(Python/JS/TS) 필터 → `internal_paths` 계산
- [x] 5.3 파일별 파서 디스패치(언어 기반), import 추출 → resolve → Edge 생성
- [x] 5.4 SyntaxError 경고는 stderr로 1줄씩
- [x] 5.5 `src/codexray/graph/serialize.py` — `to_json(graph: Graph) -> str` (스키마 v1, sorted, 들여쓰기 2)
- [x] 5.6 노드/엣지 결정론적 정렬 적용
- [x] 5.7 단위 테스트 — 다파일 internal 엣지 / external 분류 / 정렬 안정성

## 6. CLI 통합

- [x] 6.1 `src/codexray/cli.py`에 `graph` 서브커맨드 추가
- [x] 6.2 경로 검증 — 미존재·디렉토리 아님은 stderr + non-zero exit (`inventory`와 동일 패턴 재사용)
- [x] 6.3 정상 흐름 — `build_graph` → `to_json` → `print`
- [x] 6.4 단위 테스트 — `typer.testing.CliRunner`로 임시 트리에 대해 JSON 파싱 가능성·키 존재 검증

## 7. 검증

- [x] 7.1 통합 테스트 — Python 자기참조 픽스처: `tests/test_graph_build.py::test_python_self_reference`로 internal 엣지 정확히 검증
- [x] 7.2 통합 테스트 — TS 픽스처: `tests/test_graph_build.py::test_typescript_mix` + `tests/test_graph_cli.py`로 internal/external 판정 검증
- [x] 7.3 결정론 회귀 테스트 — `test_deterministic_output` + 자기 자신 실행 2회 stdout 바이트 일치
- [x] 7.4 CodeXray 자기 자신에 실측 — 0.21s (5초 예산의 24배 마진), `docs/validation/graph-first-run.md`에 캡처
- [x] 7.5 `openspec validate add-dependency-graph` 통과 재확인
- [x] 7.6 `ruff check` + `pytest` 모두 통과

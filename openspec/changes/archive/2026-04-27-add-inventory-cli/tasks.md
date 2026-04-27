## 1. 프로젝트 부트스트랩

- [x] 1.1 `pyproject.toml` 작성 — Python 3.11+, 패키지명 `codexray`, 진입점 `codexray = "codexray.cli:app"`
- [x] 1.2 의존성 선언 — `typer`, `rich`, `pathspec`
- [x] 1.3 dev 의존성 — `pytest`, `pytest-cov`, `ruff`
- [x] 1.4 `uv` 환경 초기화 + 락파일 생성, `README.md`에 1줄 실행 예시 추가
- [x] 1.5 패키지 디렉토리 스캐폴드 — `src/codexray/__init__.py`, `src/codexray/cli.py`

## 2. 파일 워킹 + 무시 규칙

- [x] 2.1 `src/codexray/walk.py` — `walk(root: Path) -> Iterator[Path]` 정의
- [x] 2.2 기본 무시 디렉토리 상수 정의 (`.git`, `node_modules`, `dist`, `build`, `venv`, `.venv`, `__pycache__`, `.next`, `target`)
- [x] 2.3 `.gitignore` 로딩 — `pathspec.PathSpec.from_lines("gitignore", ...)`로 루트 `.gitignore` 우선 처리, 없으면 빈 spec
- [x] 2.4 심볼릭 링크 비추적 (`os.scandir` + `entry.is_dir(follow_symlinks=False)` 또는 `Path.walk(follow_symlinks=False)`)
- [x] 2.5 단위 테스트 — 기본 무시 / `.gitignore` 매칭 / `.gitignore` 부재 / 심볼릭 링크 4가지 시나리오 (spec 시나리오와 1:1 대응)

## 3. 언어 분류

- [x] 3.1 `src/codexray/language.py` — 확장자 → 언어 매핑 테이블 단일 dict로 정의
- [x] 3.2 `classify(path: Path) -> str | None` — 매핑에 없으면 `None` 반환
- [x] 3.3 단위 테스트 — 매핑된 확장자 / 매핑 없는 확장자 / 대소문자 동작

## 4. LoC 카운터

- [x] 4.1 `src/codexray/loc.py` — `count_nonempty_lines(path: Path) -> int`
- [x] 4.2 바이너리 안전성 — `errors="ignore"`로 디코드, 디코드 실패 라인은 0으로 처리
- [x] 4.3 단위 테스트 — 빈 파일 / 빈 줄 포함 / 공백만 있는 줄 / 비-UTF8 바이트

## 5. 집계 + 표 출력

- [x] 5.1 `src/codexray/inventory.py` — `aggregate(root: Path) -> list[Row]` (Row: language/file_count/loc/last_modified_at)
- [x] 5.2 mtime 최댓값 계산 + ISO-8601 로컬 타임존 포맷
- [x] 5.3 `loc` 내림차순 정렬
- [x] 5.4 `src/codexray/render.py` — `rich.table.Table`로 4컬럼 표 출력, 빈 결과는 헤더만 출력
- [x] 5.5 단위 테스트 — 다국어 정렬 / LoC 합산 / 빈 코드베이스

## 6. CLI 통합

- [x] 6.1 `src/codexray/cli.py` — `typer.Typer()` 앱, `inventory` 서브커맨드 정의
- [x] 6.2 경로 검증 — 미존재·디렉토리 아님·접근 불가에 stderr 메시지 + non-zero exit
- [x] 6.3 인수 누락 시 typer 기본 usage 메시지 + non-zero exit 동작 확인
- [x] 6.4 정상 흐름 — walk → classify → aggregate → render

## 7. 검증

- [x] 7.1 통합 테스트 — 임시 디렉토리에 가짜 트리 생성 후 `codexray inventory <tmp>` 실행, stdout 표 행 검증 (스냅샷)
- [x] 7.2 사용자의 작은 게임 프로젝트로 실측 — 5초 내 표 출력 확인, 결과를 `docs/validation/inventory-first-run.md`에 캡처
- [x] 7.3 `openspec validate add-inventory-cli` 통과 재확인
- [x] 7.4 `ruff check` + `pytest` 모두 통과

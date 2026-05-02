## ADDED Requirements

### Requirement: PyPI 패키지 설치 가능

The project SHALL be installable from PyPI as a single command (`pip install codexray` or `uv tool install codexray`). The installed package SHALL include the React frontend build artifact (`frontend/dist/`) so that `codexray serve` works without additional setup. Installation SHALL succeed on Linux, macOS, and Windows for Python 3.11 and above.

#### Scenario: 패키지 메타데이터 PyPI 호환
- **WHEN** `pyproject.toml` 이 검사되면
- **THEN** `[project]` 테이블은 `name`, `version`, `description`, `readme`, `license`, `authors`, `requires-python` 필수 필드를 포함하고, `[project.urls]` 에 Repository / Issues 링크가 있으며, `classifiers` 에 OS / Python 버전 / Topic / License / Development Status 분류가 있고, `keywords` 가 1 개 이상이다

#### Scenario: 빌드 산출물에 frontend/dist 포함
- **WHEN** `uv build` 가 실행되어 wheel 이 생성되면
- **THEN** wheel 은 `frontend/dist/index.html` 과 그 모든 자산 (JS, CSS, 기타) 을 패키지 내부 경로 (예: `codexray/_frontend/`) 에 포함한다. 별도 npm install 없이 설치 후 `codexray serve` 가 SPA 를 서빙할 수 있다

#### Scenario: README 에 OS 별 설치 가이드
- **WHEN** README 가 검사되면
- **THEN** README 는 *Quickstart 위쪽* 에 "## 설치" 섹션을 포함하고, Windows / macOS / Linux 공통 명령 (`pip install codexray` 또는 `uv tool install codexray`) 과 prerequisite (Python 3.11+, 선택적 codex/claude CLI) 안내를 갖는다

#### Scenario: 빌드 검증 절차 문서화
- **WHEN** PyPI publish 직전에 빌드를 검증하면
- **THEN** 다음 절차가 README 또는 docs 에 명시되어 있다: (1) `cd frontend && npm run build`, (2) `uv build`, (3) `unzip -l dist/codexray-*.whl` 로 frontend 자산 포함 확인, (4) 임시 venv 에 wheel 설치 + `codexray --help` 동작 확인

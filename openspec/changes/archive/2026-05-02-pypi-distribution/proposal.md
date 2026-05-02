## Why

`cross-platform-ci-setup` 으로 3 OS 동작 보장 게이트는 확립됐다. 이제 *배포 가능 상태* 를 만들어야 사용자 페르소나 1순위 (전부 Windows 동료) 가 `pip install codexray` 한 줄로 설치할 수 있다. 현 `pyproject.toml` 은 *최소 동작* 형태 — PyPI 가 요구하는 메타데이터 (URLs, classifiers, keywords) 가 누락돼 있고, 프론트엔드 빌드 산출물 (`frontend/dist/`) 의 wheel 포함 여부도 결정 안 됨.

본 변경은 *배포 가능 상태 만들기* 까지 — pyproject 메타데이터 보강 + README OS 별 설치 가이드 + 빌드 검증. **실제 PyPI publish 는 사용자 계정/토큰 필요해서 본 변경 범위 밖**. 사용자가 토큰 발급 후 `uv publish` 한 줄로 publish 가능한 상태가 종착점.

## What Changes

- **pyproject.toml 메타데이터 보강**:
  - `[project.urls]` — Homepage / Repository / Issues 추가
  - `[project]` 에 classifiers 추가 (Development Status, Intended Audience, License, OS, Python version, Topic)
  - `[project]` 에 keywords 추가 (code-analysis, vibe-coding, ai-assisted-development 등)
- **frontend/dist 배포 처리 결정**:
  - 옵션 A: wheel 에 포함 — `npm run build` 산출물을 `src/codexray/web/static/` 같은 위치로 옮기고 `[tool.hatch.build]` 에 포함. `codexray serve` 가 PyPI 설치 후에도 동작.
  - 옵션 B: wheel 에서 제외 — pip 사용자는 CLI 만 쓰고, web UI 쓰려면 git clone + `npm run build` 별도 안내. 패키지 작아짐.
  - design.md 에서 결정.
- **README 에 "설치 — pip 한 줄" 섹션 추가**:
  - Windows / macOS / Linux 각 OS 의 prerequisite (Python 버전, 선택적 codex/claude CLI)
  - `pip install codexray` 또는 `uv tool install codexray` 명령
  - 설치 후 첫 실행 (`codexray --help`, `codexray dashboard <path>`, `codexray serve`) 안내
- **빌드 검증**:
  - `uv build` 로 wheel + sdist 생성, 출력 검사
  - 생성된 wheel 의 `RECORD` 파일에 frontend/dist (옵션 A 채택 시) 또는 누락 (옵션 B) 확인
- **(선택) GitHub Actions release workflow** — 본 변경에서 *workflow 파일만 추가, 실제 publish 는 사용자 토큰 추가 후* — 작업량 보고 design 단계에서 결정. 본 변경 범위에 안 넣을 가능성 높음.

## Capabilities

### New Capabilities
없음. PyPI 배포는 *어떤 capability 도 변경하지 않음* — 단지 *동일 capability 를 다른 채널로 배포할 뿐*.

### Modified Capabilities
- `web-ui`: ADDED 1 개 — 도구가 PyPI 패키지 (`pip install codexray`) 로 설치 가능해야 한다는 요구사항. frontend/dist 배포 처리 정책도 함께 spec 화.

## Impact

- **신규/변경 파일**:
  - `pyproject.toml` — 메타데이터 보강 (변경)
  - `README.md` — 설치 섹션 추가 (변경)
  - `src/codexray/web/static/` 또는 `frontend/dist/` 의 wheel 포함 처리 — 옵션 A 선택 시 빌드 셋업 변경
- **테스트**: 320 유지 (회귀 차단)
- **외부 의존성**: 없음. 빌드 도구는 `hatchling` 그대로
- **사용자 가시 변화**: PyPI publish 후 (사용자 직접 단계) `pip install codexray` 작동
- **시간 비용**: 메타데이터 정비 + README 작성 + uv build 검증 ~ 1 시간. 옵션 A 의 frontend wheel 포함은 빌드 셋업 디버깅 시간 변동

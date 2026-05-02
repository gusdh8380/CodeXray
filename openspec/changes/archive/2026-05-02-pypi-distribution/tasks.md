## 1. pyproject.toml 메타데이터 보강

- [x] 1.1 `[project.urls]` 섹션 추가 — Homepage / Repository / Issues
- [x] 1.2 `[project]` 에 `keywords` 추가 (code-analysis, vibe-coding, ai-assisted-development 등 4-6 개)
- [x] 1.3 `[project]` 에 `classifiers` 추가 — Development Status 4-Beta, License MIT, Operating System OS Independent, Python 3.11/12/13/14, Intended Audience Developers, Topic Quality Assurance + Documentation
- [x] 1.4 `requires-python = ">=3.11"` 유지 (이미 정확)

## 2. frontend/dist 의 wheel 포함 셋업

- [x] 2.1 `[tool.hatch.build.targets.wheel]` 에 `frontend/dist/` 를 패키지 내부 경로로 force-include 하는 셋업 추가 (예: `codexray/_frontend/`)
- [x] 2.2 `src/codexray/web/app.py` 의 정적 파일 마운트가 패키지 내부 위치 (`codexray/_frontend/`) 도 찾도록 fallback 로직 추가 — 개발 중에는 `frontend/dist/`, 설치 후에는 `codexray/_frontend/`
- [x] 2.3 `cd frontend && npm run build` 로 dist 최신 보장
- [x] 2.4 `uv build` 실행 → `dist/codexray-0.1.0-py3-none-any.whl` 생성 확인
- [x] 2.5 `unzip -l dist/codexray-*.whl | grep -E "_frontend|index.html"` 로 frontend 자산 포함 검증

## 3. 임시 venv 설치 검증

- [x] 3.1 `python3.14 -m venv /tmp/codexray-test-venv` 로 임시 venv
- [x] 3.2 `/tmp/codexray-test-venv/bin/pip install dist/codexray-*.whl`
- [x] 3.3 `codexray --help` → 동작 확인
- [x] 3.4 `codexray dashboard /tmp` → self-contained HTML 생성 확인
- [x] 3.5 `codexray serve --no-browser` → 8080 listening 확인 + http://127.0.0.1:8080/ 가 SPA 응답하는지 brief curl 점검

## 4. README 설치 섹션 추가

- [x] 4.1 README 에 `## 설치` 섹션 추가 (CI badge 다음, Quickstart 위)
- [x] 4.2 OS 공통 `pip install codexray` + uv `uv tool install codexray` 안내
- [x] 4.3 Prerequisite — Python 3.11+, 선택적 codex/claude CLI (각 OS 별 brew/winget/scoop/manual)
- [x] 4.4 설치 후 첫 실행 안내 — `codexray --help`, `codexray dashboard <path>`, `codexray serve`
- [x] 4.5 기존 `## Quickstart` 섹션 (git clone + uv sync) 은 *개발자용* 표시로 유지 또는 `## Development` 으로 이동

## 5. 검증 + 문서화

- [x] 5.1 `uv run pytest tests/ -q` 통과 (회귀 차단)
- [x] 5.2 `cd frontend && npm run build` 통과
- [x] 5.3 `openspec validate pypi-distribution --strict` 통과
- [x] 5.4 `docs/validation/pypi-distribution-results.md` 작성 — wheel 빌드 결과 / 임시 venv 설치 검증 캡처 / README 변경 diff 요약
- [x] 5.5 CLAUDE.md "Current Sprint" 갱신 — 본 변경 결과 + 사용자 직접 publish 절차 안내 (PyPI 토큰 발급 + `uv publish`)
- [x] 5.6 git commit (atomic 단위)

## 6. Archive

- [x] 6.1 `openspec archive pypi-distribution`
- [x] 6.2 archive 후 main spec 동기화 확인 — web-ui 에 ADDED 1 개 반영
- [x] 6.3 git push origin main

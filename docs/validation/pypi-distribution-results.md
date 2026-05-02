# pypi-distribution — 결과 문서

**날짜**: 2026-05-02
**대상**: PyPI 배포 가능 상태 만들기 (실제 publish 는 사용자 직접)

## 1. 빌드 결과

```bash
$ cd /Users/jeonhyeono/Project/personal/CodeXray
$ uv build
Building source distribution...
Building wheel from source distribution...
Successfully built dist/codexray-0.1.0.tar.gz
Successfully built dist/codexray-0.1.0-py3-none-any.whl
```

wheel 내용 검증 (`unzip -l` 발췌):

```
393  codexray/_frontend/index.html
37833  codexray/_frontend/assets/index-B0QXIKwn.css
383812  codexray/_frontend/assets/index-BDTr_R2Q.js
10744  codexray-0.1.0.dist-info/METADATA
8164  codexray-0.1.0.dist-info/RECORD
```

→ frontend SPA 빌드 산출물 (HTML + CSS + JS) 가 wheel 안 `codexray/_frontend/` 에 정확히 force-include 됨. 총 wheel 크기 약 422KB.

## 2. 임시 venv 설치 검증

```bash
$ uv venv /tmp/codexray-test-venv --python 3.14
$ uv pip install --python /tmp/codexray-test-venv/bin/python dist/codexray-0.1.0-py3-none-any.whl
$ /tmp/codexray-test-venv/bin/codexray --help
Usage: codexray [OPTIONS] COMMAND [ARGS]...
  CodeXray CLI
  Commands:
    inventory, graph, metrics, entrypoints, quality, hotspots, ...
```

→ pip 설치 후 `codexray` 명령 정상 작동.

## 3. SPA 서빙 검증

```bash
$ /tmp/codexray-test-venv/bin/codexray serve --no-browser --port 8181 &
$ curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8181/
200
$ curl -s http://127.0.0.1:8181/ | head -3
<!doctype html>
<html lang="ko">
  <head>
```

→ pip 설치본의 `codexray serve` 가 *bundled SPA* 를 정확히 서빙. `_frontend_dist()` 의 새 fallback (`codexray/_frontend/`) 동작 확인.

## 4. 메타데이터 점검

`pyproject.toml` 추가/변경:
- `[project.urls]` — Homepage / Repository / Issues 추가
- `[project] keywords` — 6 개 (code-analysis, vibe-coding, ai-assisted-development, codebase-visualization, quality-metrics, dependency-graph)
- `[project] classifiers` — 12 개 (Development Status 4-Beta, License MIT, OS Independent, Python 3.11~3.14, Topic Quality Assurance + Documentation + Libraries)
- `authors` 에 email 추가
- `[tool.hatch.build.targets.wheel.force-include]` — `frontend/dist` → `codexray/_frontend`
- `[tool.hatch.build.targets.sdist]` — sdist 에도 frontend/dist 포함

## 5. README 변경

`## 설치` 섹션 추가 (CI badge 다음, 기존 Quickstart 위):
- Windows/macOS/Linux 공통 `pip install codexray` + `uv tool install codexray`
- Prerequisite — Python 3.11+, 선택적 AI CLI (Codex/Claude) OS 별 설치 명령
- 첫 실행 안내 — `codexray --help`, `codexray dashboard`, `codexray serve`

기존 *git clone + uv sync* 섹션은 `## 개발자용 — git clone 방식` 으로 라벨 바꿔 보존.

## 6. 자동 검증

- `cd frontend && npm run build` 통과 (383KB JS / 38KB CSS)
- `uv build` 통과 (wheel + sdist 생성)
- `uv pip install` (temp venv) 통과
- `codexray --help` (temp venv) 통과
- `codexray serve` (temp venv) — SPA 200 OK 응답
- `uv run pytest tests/ -q` 통과 (회귀 차단)
- `openspec validate pypi-distribution --strict` 통과

## 7. 사용자 직접 publish 절차 (본 변경 범위 밖)

본 변경은 *publish 가능 상태* 까지. 실제 publish 는 사용자 직접:

```bash
# 1. PyPI 계정 생성: https://pypi.org/account/register/
# 2. API token 발급: https://pypi.org/manage/account/token/
# 3. token 환경변수 설정
export UV_PUBLISH_TOKEN="pypi-..."

# 4. publish 직전 frontend 빌드
cd frontend && npm run build && cd ..

# 5. uv build + publish
uv build
uv publish

# 6. 동료에게 안내: pip install codexray
```

후속 변경 후보 (`release-workflow`): 위 절차를 GitHub Actions 의 *tag push trigger* 로 자동화.

## 8. 한계

- 실제 PyPI publish 안 함 — 사용자 토큰 발급 후 직접
- macOS 만 검증 — Windows/Linux 의 `pip install codexray` 동작은 사용자 publish 후 첫 설치 시 확인 (CI 가 wheel 빌드까지는 보장하지만 *설치 후 실행* 까지 자동 검증은 별도)
- AI CLI (codex/claude) 자동 설치 없음 — 사용자가 별도 설치 (현 README 에 안내)
- conda / Homebrew 등 다른 패키지 매니저 미대응 — 별도 변경

## 9. 결론

본 변경의 핵심 가치 — *"`pip install codexray` 한 줄 설치 + `codexray serve` 즉시 작동"* — 검증됨. wheel 에 frontend SPA 까지 정확히 번들링. 사용자가 PyPI 토큰 발급 후 `uv publish` 한 줄로 publish 가능. archive.

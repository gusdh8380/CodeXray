## Context

Phase 1 (cross-platform-ci-setup) 으로 3 OS pytest 통과 게이트가 확립됐다. 이제 동료 (전부 Windows) 가 *어떻게 설치하는가* 를 풀어야 한다. 가장 매끄러운 길은 PyPI 배포 — `pip install codexray` 한 줄. 그러나 본 도구는 *web UI (React SPA)* 를 핵심 인터페이스로 가져가는데, 이게 별도 빌드 산출물 (`frontend/dist/`) 에 의존한다. PyPI 패키지에 이걸 어떻게 넣을지가 본 변경의 핵심 결정.

## Goals / Non-Goals

**Goals:**
- pyproject.toml 이 PyPI publish 가능한 형태 (메타데이터 충실 + 빌드 정상)
- `pip install codexray` 후 `codexray serve` 가 *동료 환경* 에서 동작 (frontend SPA 까지 노출)
- README 에 OS 별 설치법 + prerequisite 명확
- `uv build` 로 wheel + sdist 정상 생성

**Non-Goals:**
- 실제 PyPI publish — 사용자 PyPI 계정/토큰 발급 필요
- conda / Homebrew / chocolatey 등 다른 매니저
- PyInstaller 바이너리 패키징
- AI 어댑터 (codex / claude CLI) 자동 설치 — 사용자가 별도 설치 (현재 README 와 동일)
- frontend dev server (`npm run dev`) PyPI 통합 — production 빌드만

## Decisions

### 결정 1: frontend/dist 를 wheel 에 포함 (옵션 A 채택)

`codexray serve` 의 핵심 가치가 *web UI 시각화* 인데 이게 빠지면 PyPI 사용자에게 *반쪽짜리 도구*. 동료 페르소나는 *비개발자* 라 `git clone + npm install + npm run build` 같은 추가 단계 못함. wheel 에 dist 포함이 유일한 길.

**구현**:
- `frontend/dist/*` 를 `src/codexray/web/static/` 으로 옮기지 *않고*, hatchling 의 `[tool.hatch.build]` 에 `include` 패턴 추가
- 또는 `tool.hatch.build.targets.wheel` 의 `force-include` 사용해 frontend/dist 를 wheel 안 특정 경로 (`codexray/_frontend/`) 로 매핑
- web-ui 의 정적 서빙 코드 (`app.py` 의 StaticFiles 마운트) 는 *런타임에* 패키지 위치 기준으로 dist 찾도록 (이미 그래야 정상 — 확인)

**대안 — 옵션 B (제외)**:
- pip 사용자는 CLI 만 쓰고 web UI 못 씀
- 동료가 못 씀 — 페르소나 1순위 깨짐
- 기각

**위험**:
- wheel 크기 증가 (dist 의 JS+CSS 약 420KB)
- npm build 안 한 상태에서 `uv build` 시 dist 부재 → wheel 에 빈 폴더 또는 에러
- 해결: README 에 *publish 전 `cd frontend && npm run build` 필수* 명시

### 결정 2: classifiers / keywords / urls 표준 셋

PyPI 가 권장하는 메타데이터:

```toml
[project]
keywords = ["code-analysis", "vibe-coding", "ai-assisted-development", "codebase-visualization"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "Programming Language :: Python :: 3.14",
    "Topic :: Software Development :: Quality Assurance",
    "Topic :: Software Development :: Documentation",
]

[project.urls]
Homepage = "https://github.com/gusdh8380/CodeXray"
Repository = "https://github.com/gusdh8380/CodeXray"
Issues = "https://github.com/gusdh8380/CodeXray/issues"
```

`Development Status :: 4 - Beta` — 외부 검증 (non-roboco-validation) 까지 끝난 상태라 4-Beta 가 정직.

### 결정 3: README 설치 섹션 위치 + 형식

위치: `# CodeXray` heading + CI badge 다음, *현재 Quickstart 위*.

형식:
```markdown
## 설치

### Windows / macOS / Linux 공통

\`\`\`bash
pip install codexray
\`\`\`

또는 uv 사용자:

\`\`\`bash
uv tool install codexray
\`\`\`

### Prerequisite

- Python 3.11+ ([python.org](https://python.org) 에서 설치)
- (선택) AI 정성 평가용: Codex CLI 또는 Claude Code CLI ...
\`\`\`
```

기존 *git clone + uv sync* 섹션은 *개발자용* 으로 위치 이동 (Development 섹션 안).

### 결정 4: GitHub Actions release workflow 는 본 변경에서 *추가 안 함*

이유:
- workflow 파일 추가는 30 분 작업이지만, *실제 동작 확인* 은 사용자가 토큰 발급 후. 본 변경 안에서 검증 못 함.
- 검증 안 된 workflow 를 main 에 두면 누군가 우연히 tag push 시 의도치 않게 publish 시도 (실패하지만 noisy)
- 별도 변경 `release-workflow` 로 분리 — 사용자가 토큰 발급한 후 *실제 첫 publish 와 동시에* 추가하는 게 자연스러움

### 결정 5: 빌드 검증 방법

`uv build` 실행 후:
1. `dist/codexray-0.1.0-py3-none-any.whl` 생성 확인
2. `unzip -l` 로 wheel 내용 점검 — `codexray/_frontend/index.html` (또는 채택 위치) 포함 확인
3. 임시 venv 만들어 `pip install dist/codexray-0.1.0-py3-none-any.whl` → `codexray --help` → 동작 확인
4. `codexray dashboard <test_path>` 로 self-contained HTML 생성 확인

`codexray serve` 의 frontend 노출은 *수동 점검* — venv 에서 실행 후 브라우저 확인.

## Risks / Trade-offs

- [npm build 안 한 상태로 `uv build` → dist 빠진 wheel 배포] → README + tasks.md 에 *publish 전 frontend build 필수* 명시. 향후 release workflow 에서 자동화.
- [wheel 크기 증가 (420KB)] → 일반 OSS 도구 평균 수준. 무시.
- [classifiers 가 PyPI 카테고리에 정확히 매핑되는지] → PyPI Trove classifiers 공식 목록 참조. 수동 확인.
- [version `0.1.0` 그대로] → publish 시 첫 PyPI 버전. 버전 정책 (semver) 은 별도 결정 사안. 본 변경에서는 그대로 유지.

## Migration Plan

1. pyproject.toml 메타데이터 보강 — classifiers, keywords, urls 추가
2. hatchling 빌드 셋업에서 frontend/dist 포함 (force-include)
3. `app.py` 의 정적 파일 위치가 패키지 기준으로 정확히 dist 를 찾는지 확인 (필요 시 fix)
4. `cd frontend && npm run build` (최신 dist 보장)
5. `uv build` 실행 → wheel 검증
6. 임시 venv 에서 설치 + 동작 점검
7. README 에 설치 섹션 추가
8. CLAUDE.md 갱신 + commit + archive

롤백: pyproject.toml + README revert. wheel 빌드 셋업도 원복. 영향 범위 작음.

## Open Questions

- frontend/dist 를 wheel 에 force-include 하는 hatchling 정확한 구문 — 시도해보고 안 되면 `tool.hatch.build.hooks` 같은 추가 셋업 필요할 수도. 첫 시도가 실패하면 사용자와 상의.
- README 에 *uninstall* / *upgrade* 안내 추가할지 — 본 변경에서는 안 함. 동료가 처음 설치한 후 다른 명령 안 알려도 충분.
- macOS 의 codex CLI 가 brew 로만 설치되는데 Windows 에 codex CLI 가 *어떻게* 설치되는지 확인 필요. AI 어댑터 자동 설치는 본 변경 non-goal 이지만 README 에 정확히 안내해야 함.

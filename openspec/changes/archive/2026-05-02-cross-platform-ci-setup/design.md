## Context

사용자 페르소나 1순위 (동료) 가 *전부 Windows*. 도구는 macOS dev 환경에서만 검증. PyPI 배포 (`pypi-distribution` — 후속 변경) 전에 *Windows 동작 보장* 게이트 필수. Windows 머신 없으니 검증 수단은 *원격 CI* 만.

이 변경은 인프라 셋업이라 다른 capability 코드에 영향 거의 없음. 단 fix 가 필요하면 그 자리에서 추가 — *작업 진행 중 발견* 형태.

## Goals / Non-Goals

**Goals:**
- GitHub Actions matrix (`ubuntu-latest` + `macos-latest` + `windows-latest`) 에서 pytest 통과
- 첫 CI 결과 본 후 Windows 호환성 깨짐 *모두* fix
- 향후 변경의 자동 검증 게이트 확립

**Non-Goals:**
- PyPI 배포 셋업 (별도 변경)
- frontend `npm run build` CI 추가 — 본 변경 범위는 백엔드 pytest 만 (frontend CI 는 별도 사이클로 후속)
- E2E (Selenium / Playwright) 테스트 — 단위 테스트만
- Windows 사용자 머신에서 *실제 codexray serve* 동작 확인 — 동료 베타 단계
- 패키징 (PyInstaller 바이너리) — 별도 변경

## Decisions

### 결정 1: matrix 에 3 OS 모두 포함, 단일 Python 3.14

Python 버전 matrix 추가도 가능하지만 비용 증가. 현재 dev 환경이 3.14 라 그 한 버전만 보장. 후속 변경에서 3.12 / 3.13 추가 가능.

```yaml
strategy:
  matrix:
    os: [ubuntu-latest, macos-latest, windows-latest]
```

### 결정 2: uv 셋업은 `astral-sh/setup-uv` action 사용

표준 GitHub Actions. `uv sync` 한 줄로 의존성 셋업.

```yaml
- uses: astral-sh/setup-uv@v6
- run: uv sync --all-extras
- run: uv run pytest tests/ -q
```

### 결정 3: Windows 호환성 *예방적 fix* 안 함

CI 가 깨지기 전까지는 코드 안 건드림. 추측 fix 는 *진짜 깨지는 곳* 을 가리거나 새 버그 만들 위험. CI 결과 본 후 *명확히 깨진 것* 만 fix.

### 결정 4: fix 사이클 가시화

Windows 머신 없으니 *추측 fix → push → CI 결과 확인* 사이클. 각 사이클이 5–10 분. 사이클 횟수는 fix 의 정확성에 따라 1~3 회 예상. 사이클 결과를 검증 문서에 기록 (어떤 추측이 맞았고 틀렸는지).

### 결정 5: 첫 CI workflow 는 단순한 게 우선

복잡한 cache / matrix include / artifact upload 등은 후속에. 본 변경은 *돌리고 결과 확인* 까지가 목적. cache 추가는 CI 비용 절감 목적이라 첫 단계 아님.

### 결정 6: workflow trigger 는 push + pull_request

```yaml
on:
  push:
    branches: [main]
  pull_request:
```

forking 없는 상태에서 main push 만으로도 충분. PR trigger 추가는 미래 협업 대비.

## Risks / Trade-offs

- [Windows fix 사이클이 예상보다 길어짐] → 결정 4 의 가시화로 *몇 시간 vs 며칠* 의 분기점을 사용자와 공유. 길어지면 본 변경 범위에서 *발견된 fix 만 적용 + 미해결 항목은 후속 변경* 으로 분리.
- [pytest 가 Windows-specific 동작 (예: 임시파일 권한) 로 실패] → CI 결과로 직접 확인. 일부는 테스트 자체의 OS 가정이라 fix 가 코드 아니라 *테스트 셋업* 일 수도.
- [한국어 인코딩 cp949 이슈] → 모든 `open()` / `read_text()` 에 `encoding="utf-8"` 명시 — 이미 대부분 그렇게 돼있음 (axes.py 같은 곳). CI 로 누락 식별.
- [GitHub Actions 비용] → public repo 라 무료. 단 매 push 마다 3 OS 동시 실행으로 minutes 사용량 늘어남 — public 은 cap 없음.

## Migration Plan

1. workflow.yml 작성 → push → 첫 CI 결과 (5–10 분) 확인
2. macOS / Linux 통과 확인 (예상 — dev 환경과 거의 같음)
3. Windows 결과 분석 — 깨진 테스트 / 깨진 모듈 식별
4. fix 추측 + push → 다음 CI 결과 확인
5. 사이클 반복 — *모든 OS 통과* 까지
6. 검증 문서 작성 (사이클별 발견·fix 기록)
7. CLAUDE.md 갱신 + commit + archive

롤백: workflow.yml 삭제 + Windows fix revert. 다른 capability 영향 거의 없으므로 안전.

## Open Questions

- Windows fix 가 *예상 외로 큰 변경* 을 요구할 경우 (예: subprocess 처리 전체 재설계) 본 변경 범위 초과. 사용자와 *그 시점에* 분리 결정.
- frontend `npm run build` 도 CI 에 추가할지 — 본 변경에선 안 함. 후속 `frontend-ci` 변경.
- README 에 CI status badge 추가할지 — 본 변경에서 추가 (작은 변경, README 편집 1 줄).

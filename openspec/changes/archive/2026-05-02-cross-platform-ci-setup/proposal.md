## Why

본 도구의 사용자 페르소나 1순위인 *비개발자 동료* 는 *전부 Windows 환경* 이다. 그러나 도구 자체는 macOS 에서만 검증됐고 Windows / Linux 동작은 *추측 수준*. 동료에게 "써봐" 라고 권유하기 전에 최소한의 *동작 보장 게이트* 가 필요하다.

본 변경은 GitHub Actions 의 OS matrix CI 를 도입해 *향후 모든 변경* 이 3 OS 에서 자동 검증되도록 인프라를 깐다. PyPI 배포 (별도 변경 `pypi-distribution`) 의 *전제 조건* — Windows 에서 깨지는 도구를 PyPI 에 publish 하면 동료의 첫 경험이 즉시 깨진다.

## What Changes

- `.github/workflows/ci.yml` 신규 — `ubuntu-latest` / `macos-latest` / `windows-latest` matrix 에서 Python 3.14 + uv 셋업 + `pytest` 실행
- 첫 push 후 Windows CI 결과 보고 발견되는 *호환성 깨짐* 을 fix:
  - 가능한 후보 (실제 fix 는 CI 결과 기반):
    - subprocess 호출의 `shell=True` 또는 명령어 (예: `git`) 경로 차이
    - 한국어 텍스트 인코딩 (Windows 의 cp949 기본값 vs UTF-8)
    - pathlib `Path` 의 OS 별 동작 (resolve / 대소문자 / 구분자)
    - typer / rich 의 색상 출력 Windows 콘솔 호환성
- 검증 문서 `docs/validation/cross-platform-ci-setup-results.md` — CI 통과 캡처 + Windows fix 발견 사례 정리
- `web-ui` capability 에 ADDED 요구사항 1 개 — 도구가 OS matrix CI 에서 검증된다는 사실을 spec 으로 못 박아 회귀 차단

## Capabilities

### New Capabilities
없음.

### Modified Capabilities
- `web-ui`: ADDED 1 개 — 도구의 핵심 진입점인 web-ui 와 백엔드가 OS matrix CI (Linux / macOS / Windows) 에서 자동 검증된다는 요구사항. 이 spec 이 있으면 미래 변경에서 CI 가 통과해야 머지 가능.

## Impact

- **신규 파일**: `.github/workflows/ci.yml`, `docs/validation/cross-platform-ci-setup-results.md`
- **변경 파일**: CI 결과 본 후 결정. 0~몇 파일.
- **테스트**: 320 유지 (신규 추가 없음, 기존 통과 여부만 OS 별로 확인)
- **외부 의존성**: 없음. GitHub Actions 는 public repo 무료.
- **사용자 가시 변화**: 없음 — 인프라 변경. 다만 *향후 변경 PR* 마다 CI badge / 통과 표시가 README 에 노출 가능 (선택)
- **시간 비용**: 첫 push 후 CI 실행 5–10 분 + Windows fix 사이클 1–2 회 (추측 fix → push → 결과 확인). Windows 머신 없음.

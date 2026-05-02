## ADDED Requirements

### Requirement: 크로스 플랫폼 CI 게이트

The project SHALL maintain a GitHub Actions CI workflow that runs the full pytest suite on Linux, macOS, and Windows for every push to `main` and every pull request. All three OS jobs SHALL pass before any change is merged. This guarantees the tool's CLI and web-ui backend work on the user's primary persona's environment (Windows coworkers) without manual platform verification.

#### Scenario: CI matrix 3 OS 정의
- **WHEN** `.github/workflows/ci.yml` 가 검사되면
- **THEN** workflow 는 `strategy.matrix.os` 에 `ubuntu-latest`, `macos-latest`, `windows-latest` 셋을 모두 포함한다

#### Scenario: pytest 가 모든 OS 에서 실행됨
- **WHEN** 모든 matrix job 이 실행되면
- **THEN** 각 job 은 `uv sync` 로 의존성을 설치한 후 `uv run pytest tests/ -q` 를 실행하고 *exit code 0* 을 반환한다

#### Scenario: 한 OS 라도 실패하면 머지 차단
- **WHEN** main 브랜치로 push 되거나 pull request 가 생성되면
- **THEN** workflow 가 trigger 되고, 셋 중 하나라도 실패하면 CI 결과가 *failure* 로 보고된다 (GitHub PR UI 에서 머지 가능 상태가 아니게 됨)

#### Scenario: 신규 변경의 Windows 회귀 차단
- **WHEN** 새 변경이 main 으로 머지되기 전 PR 단계에서
- **THEN** Windows job 이 통과해야 머지 가능하다 — Windows 사용자 (1순위 페르소나) 의 첫 경험이 깨지지 않도록 자동 보장

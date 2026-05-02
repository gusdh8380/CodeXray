## ADDED Requirements

### Requirement: 신호 풀이 일반 OSS 관행을 포함

The system's vibe coding signal pools (intent / verification / continuity 축의 sub-cat 검사) SHALL include conventions used by general OSS projects, not only AI-tool-specific conventions (`CLAUDE.md`, `AGENTS.md`, `docs/intent.md`, `openspec/`, `.claude/`, `.omc/`). Specifically, the following general-OSS signals SHALL be recognized:

#### Scenario: pyproject 의 description 이 의도 신호로 인정
- **WHEN** 레포에 `pyproject.toml` 이 있고 그 `[project]` 테이블의 `description` 이 30 자 이상이거나, `description` 이 비어있지 않고 `keywords` 가 1 개 이상 있을 때
- **THEN** intent 축의 "프로젝트 의도 문서" sub-cat 이 *충족* 으로 판정된다

#### Scenario: package.json 의 description 이 의도 신호로 인정
- **WHEN** 레포에 `package.json` 이 있고 그 `description` 필드가 30 자 이상이거나, `description` 이 비어있지 않고 `keywords` 가 1 개 이상 있을 때
- **THEN** intent 축의 "프로젝트 의도 문서" sub-cat 이 *충족* 으로 판정된다

#### Scenario: README 명시 섹션 헤더가 의도 신호로 인정
- **WHEN** 레포의 README 본문 *어디에든* `## What`, `## Why`, `## Purpose`, `## About`, `## 이 프로젝트`, `## 정체`, `## 역할` 같은 명시 섹션 헤더가 존재할 때 (대소문자 무관)
- **THEN** intent 축의 "프로젝트 의도 문서" sub-cat 이 *충족* 으로 판정된다 (기존의 첫 5 단락 키워드 매칭에 추가)

#### Scenario: examples / demo / samples 디렉토리가 손 검증 신호로 인정
- **WHEN** 레포에 `examples/`, `demo/`, `samples/`, `examples-*` 패턴 디렉토리가 존재하고 *비어있지 않을 때*
- **THEN** verification 축의 "손 검증 흔적" sub-cat 이 *충족* 으로 판정된다

#### Scenario: .storybook/ 디렉토리가 손 검증 신호로 인정
- **WHEN** 레포에 `.storybook/` 디렉토리가 존재할 때
- **THEN** verification 축의 "손 검증 흔적" sub-cat 이 *충족* 으로 판정된다 (UI 컴포넌트 손 검증의 형태)

#### Scenario: MAINTAINERS / CODEOWNERS 가 핸드오프 신호로 인정
- **WHEN** 레포에 `MAINTAINERS.md`, `MAINTAINERS` (확장자 없음), `CODEOWNERS`, `.github/CODEOWNERS` 중 하나라도 존재할 때
- **THEN** continuity 축의 "핸드오프 문서" sub-cat 이 *충족* 으로 판정된다

#### Scenario: getting-started / onboarding / contributing 디렉토리가 핸드오프 신호로 인정
- **WHEN** 레포에 `docs/getting-started/`, `docs/onboarding/`, `docs/contributing/` 디렉토리 중 하나라도 존재할 때
- **THEN** continuity 축의 "핸드오프 문서" sub-cat 이 *충족* 으로 판정된다 (기존의 `CONTRIBUTING.md` 단일 파일에 추가)

### Requirement: 신호 false positive 차단을 위한 충실도 체크

The system SHALL guard new general-OSS signals against false positives by requiring minimum content thresholds where applicable.

#### Scenario: 빈 description 은 의도 신호로 인정 안 됨
- **WHEN** `pyproject.toml` 또는 `package.json` 의 `description` 이 빈 문자열이거나 30 자 미만이고 `keywords` 도 비어있을 때
- **THEN** intent 축의 "프로젝트 의도 문서" sub-cat 은 그 신호로 *충족 처리 되지 않는다*

#### Scenario: 빈 examples 디렉토리는 손 검증 신호로 인정 안 됨
- **WHEN** `examples/` 또는 `demo/` 디렉토리가 존재하지만 *내부 파일이 없을 때*
- **THEN** verification 축의 "손 검증 흔적" sub-cat 은 그 신호로 *충족 처리 되지 않는다*

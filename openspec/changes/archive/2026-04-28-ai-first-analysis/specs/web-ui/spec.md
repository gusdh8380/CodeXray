## ADDED Requirements

### Requirement: AI-first briefing loading UX
The system SHALL show step-by-step progress while briefing analysis runs, so the user knows what is happening during the 30-90 second wait.

#### Scenario: 단계별 진행 메시지 표시
- **WHEN** /api/briefing background job이 실행 중이면
- **THEN** 결과 패널은 현재 단계("Python 분석 중...", "증거 수집 완료", "AI 해석 중...", "완료")를 polling 응답마다 갱신해서 표시한다

#### Scenario: 빈 화면 없음
- **WHEN** 분석이 시작된 후 결과가 나오기 전까지
- **THEN** 결과 패널은 빈 화면 대신 진행 상태를 항상 표시한다

### Requirement: AI 해석 결과 폴백
The system SHALL display deterministic briefing content with a notice when AI interpretation is unavailable.

#### Scenario: AI 어댑터 미설정 시 폴백
- **WHEN** claude 또는 codex CLI 어댑터가 모두 사용 불가능한 상태에서 Briefing을 실행하면
- **THEN** 시스템은 기존 결정론적 Briefing을 표시하고 상단에 "AI 해석 없이 표시 중" 배너를 보여준다

#### Scenario: AI 호출 실패 시 폴백
- **WHEN** AI 호출이 실패하면
- **THEN** 시스템은 기존 결정론적 Briefing을 표시하고 오류 배너를 표시한다

## MODIFIED Requirements

### Requirement: Briefing endpoint
The system SHALL provide a web endpoint that renders the codebase briefing for the selected repository, using AI interpretation as the primary output when AI is available.

#### Scenario: Valid path briefing request
- **WHEN** a valid repository path is submitted to the briefing endpoint
- **THEN** the web UI starts a background job and immediately returns a polling fragment with step progress

#### Scenario: Briefing job completion with AI
- **WHEN** the briefing background job completes and AI interpretation is available
- **THEN** the system returns an HTTP 200 fragment containing AI-generated comprehensive analysis covering executive summary, architecture, quality risk, and next actions

#### Scenario: Briefing job completion without AI
- **WHEN** the briefing background job completes and AI interpretation is unavailable
- **THEN** the system returns an HTTP 200 fragment with the deterministic briefing and an "AI 해석 없이 표시 중" notice

#### Scenario: Briefing includes git-history build process
- **WHEN** git history is available for the selected repository
- **THEN** the rendered briefing includes a How It Was Built section with commit timeline and vibe-coding process evidence

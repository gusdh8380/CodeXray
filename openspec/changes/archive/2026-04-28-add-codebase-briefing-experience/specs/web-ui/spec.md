## ADDED Requirements

### Requirement: Briefing-first web navigation
The system SHALL organize the web UI around presentation-like briefing sections before low-level analyzer tabs.

#### Scenario: Primary briefing sections appear
- **WHEN** the browser loads the web UI main page
- **THEN** the primary navigation includes Briefing, Architecture, Quality & Risk, How It Was Built, Explain, and Deep Dive sections

#### Scenario: Detailed analyzers remain accessible
- **WHEN** the user opens the Deep Dive section
- **THEN** the UI still exposes the existing detailed analysis views for inventory, graph, metrics, hotspots, quality, entrypoints, report, dashboard, review, and vibe-coding evidence

### Requirement: Briefing endpoint
The system SHALL provide a web endpoint that renders the codebase briefing for the selected repository.

#### Scenario: Valid path briefing request
- **WHEN** a valid repository path is submitted to the briefing endpoint
- **THEN** the web UI returns an HTTP 200 fragment containing a presentation-like briefing with executive, architecture, risk, build-process, explanation, and deep-dive sections

#### Scenario: Briefing includes git-history build process
- **WHEN** git history is available for the selected repository
- **THEN** the rendered briefing includes a How It Was Built section with commit timeline and vibe-coding process evidence

### Requirement: Non-developer friendly rendering
The system SHALL render briefing content in readable Korean for both technical and non-technical audiences.

#### Scenario: Plain-language explanation appears
- **WHEN** the Explain section is rendered
- **THEN** it includes plain-language text suitable for explaining the repository to a non-developer

#### Scenario: Evidence remains visible
- **WHEN** a briefing section presents an interpretation
- **THEN** nearby UI includes concrete evidence such as grade, paths, commit messages, or process artifacts

### Requirement: Briefing validation capture
The system SHALL capture briefing validation results for both validation codebases.

#### Scenario: Validation documents
- **WHEN** add-codebase-briefing-experience implementation validation is complete
- **THEN** `docs/validation/codebase-briefing-self.md` and `docs/validation/codebase-briefing-civilsim.md` contain representative briefing output summaries

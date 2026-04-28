## ADDED Requirements

### Requirement: Vibe Coding tab
The system SHALL provide a Vibe Coding tab in the localhost web UI that renders the vibe-coding report for the selected repository.

#### Scenario: Tab appears on main page
- **WHEN** the browser loads the web UI main page
- **THEN** the analysis tabs include a Vibe Coding tab

#### Scenario: Vibe Coding endpoint
- **WHEN** a valid repository path is submitted to the Vibe Coding tab
- **THEN** the web UI returns an HTTP 200 fragment containing the vibe-coding report

### Requirement: Non-developer report rendering
The system SHALL render the Vibe Coding tab as a readable Korean report for non-developer vibe coders, with summary cards before technical evidence tables.

#### Scenario: Summary-first rendering
- **WHEN** the Vibe Coding tab renders a report
- **THEN** the fragment begins with confidence, strengths, risks, and next actions before listing detailed evidence

#### Scenario: Evidence remains inspectable
- **WHEN** the Vibe Coding tab renders detected artifacts
- **THEN** the fragment includes evidence paths grouped by process area

### Requirement: Vibe Coding tab validation capture
The system SHALL capture Vibe Coding tab validation results for both validation codebases.

#### Scenario: Validation documents
- **WHEN** add-vibe-coding-report-tab implementation validation is complete
- **THEN** `docs/validation/vibe-coding-report-self.md` and `docs/validation/vibe-coding-report-civilsim.md` contain representative output summaries

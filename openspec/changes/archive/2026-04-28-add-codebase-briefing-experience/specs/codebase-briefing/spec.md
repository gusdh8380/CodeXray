## ADDED Requirements

### Requirement: Briefing composition
The system SHALL build a codebase briefing model by composing existing deterministic analysis results and vibe-coding process evidence.

#### Scenario: Briefing model contains presentation sections
- **WHEN** a valid repository path is analyzed
- **THEN** the briefing result includes sections for executive summary, architecture, quality and risk, how it was built, non-developer explanation, and deep dive references

#### Scenario: Briefing uses existing analyzers
- **WHEN** the briefing result is built
- **THEN** it includes evidence derived from inventory, graph, metrics, entrypoints, quality, hotspots, summary, and vibe-coding report outputs

### Requirement: Git-history creation process analysis
The system SHALL analyze git history as evidence for how the repository was created, especially from a vibe-coding workflow perspective.

#### Scenario: Git timeline available
- **WHEN** the target path is inside a git repository
- **THEN** the briefing includes commit count, recent commit messages, commit type distribution, and a creation-process timeline summary

#### Scenario: Vibe-coding process commits detected
- **WHEN** git history contains commits or changed paths for OpenSpec, validation documents, retrospectives, handoff documents, `AGENTS.md`, `CLAUDE.md`, `.omc`, `.roboco`, or `.claude`
- **THEN** the briefing classifies those commits as vibe-coding process evidence and cites the commit hash, message, and path category

#### Scenario: Git history unavailable
- **WHEN** the target path is not inside a git repository or git history cannot be read within the timeout
- **THEN** the briefing still returns successfully and marks creation history as unavailable

### Requirement: Presentation-like narrative
The system SHALL produce briefing text that can be read like a developer-prepared analysis deck while retaining evidence links.

#### Scenario: Shareable team summary
- **WHEN** the briefing renders the executive section
- **THEN** it includes a concise team-shareable explanation of what the repository appears to be, current status, strongest evidence, top risk, and next action

#### Scenario: Non-developer explanation
- **WHEN** the briefing renders the explanation section
- **THEN** it describes the repository in plain language without requiring knowledge of graph, fan-in, SCC, or hotspot terminology

### Requirement: Deep-dive preservation
The system SHALL preserve access to detailed analyzer outputs from the briefing experience.

#### Scenario: Deep-dive references
- **WHEN** the briefing renders deep-dive information
- **THEN** it references available detailed views for inventory, graph, metrics, hotspots, quality, entrypoints, report, dashboard, review, and vibe-coding evidence

### Requirement: Deterministic briefing serialization
The system SHALL serialize briefing data with `schema_version: 1`, deterministic ordering, and root-relative POSIX paths where paths are present.

#### Scenario: Repeatable briefing
- **WHEN** the same repository is analyzed twice without file or git-history changes
- **THEN** the serialized briefing bytes are identical

### Requirement: Briefing performance budget
The system SHALL complete deterministic briefing analysis within 5 seconds on the validation codebases when git history commands complete within their timeout.

#### Scenario: Self validation
- **WHEN** CodeXray repository path is analyzed
- **THEN** the briefing completes within 5 seconds and includes git-history evidence for the project's OpenSpec, validation, and vibe-coding process artifacts

#### Scenario: CivilSim validation
- **WHEN** CivilSim repository path is analyzed
- **THEN** the briefing completes within 5 seconds or returns a graceful history-unavailable marker while still rendering meaningful repository status

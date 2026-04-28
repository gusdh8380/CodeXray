# codebase-briefing Specification

## Purpose
The codebase-briefing capability composes CodeXray's deterministic analyzers into a presentation-like repository briefing that explains what the codebase is, its current status, how it was built, key risks, and next actions. It combines inventory, graph, metrics, entrypoints, quality, hotspots, summary, vibe-coding evidence, and git-history creation-process analysis, then feeds the web UI Briefing experience while preserving deep-dive access to the underlying analyzers.
## Requirements
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

### Requirement: Briefing presentation slides
The system SHALL build deterministic presentation slide data from the existing codebase briefing evidence.

#### Scenario: Slide set contains audience-ready sections
- **WHEN** a valid repository path is analyzed
- **THEN** the briefing result includes presentation slides for opening summary, system shape, current health, build history, explanation for non-developers, and recommended next actions

#### Scenario: Slides cite concrete evidence
- **WHEN** presentation slides are built
- **THEN** each slide includes at least one concrete evidence item such as grade, path, metric, hotspot, commit message, or process artifact

#### Scenario: Presenter summary exists
- **WHEN** the briefing result is built
- **THEN** it includes a concise presenter summary suitable for reading aloud to a teammate or non-developer stakeholder

### Requirement: Presentation serialization
The system SHALL serialize presentation slide data with `schema_version: 1`, deterministic ordering, and root-relative POSIX paths where paths are present.

#### Scenario: Repeatable presentation serialization
- **WHEN** the same repository is analyzed twice without file or git-history changes
- **THEN** the serialized briefing presentation fields are byte-for-byte identical

### Requirement: Presentation depth preservation
The system SHALL preserve deep analysis access from the presentation briefing.

#### Scenario: Slides point to deep dives
- **WHEN** a presentation slide summarizes architecture, quality, hotspots, build process, or next actions
- **THEN** it includes references to the relevant detailed analyzer or briefing section that can be used to inspect the underlying evidence

### Requirement: Deep briefing interpretation
The system SHALL build each briefing presentation slide with deterministic interpretation fields that explain meaning, risk, and next action.

#### Scenario: Slide includes interpretation fields
- **WHEN** a valid repository path is analyzed
- **THEN** each presentation slide includes summary, meaning, risk, and action text derived from analyzer evidence

#### Scenario: Interpretation remains evidence-backed
- **WHEN** a slide contains meaning, risk, or action text
- **THEN** the slide includes concrete evidence such as grade, score, path, count, commit, or process artifact supporting that interpretation

### Requirement: Creation story analysis
The system SHALL interpret git-history and vibe-coding evidence as a repository creation story.

#### Scenario: Git and process evidence available
- **WHEN** git history or vibe-coding process artifacts are available
- **THEN** the briefing explains the observed creation workflow, including whether agent guidance, OpenSpec, validation, retrospectives, or handoff artifacts appear

#### Scenario: Process evidence unavailable
- **WHEN** git history and vibe-coding process evidence are unavailable
- **THEN** the briefing states that creation-process confidence is limited and recommends validating the project history manually

### Requirement: Plain-language technical translation
The system SHALL translate structural and quality signals into plain language suitable for non-developers.

#### Scenario: Architecture translation
- **WHEN** graph or metrics evidence is present
- **THEN** the briefing explains whether the codebase appears small, centralized, tangled, or broad in plain language

#### Scenario: Quality translation
- **WHEN** quality and hotspot evidence is present
- **THEN** the briefing explains the practical implication of the grade and top risk files without requiring metric terminology


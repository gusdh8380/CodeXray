## ADDED Requirements

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

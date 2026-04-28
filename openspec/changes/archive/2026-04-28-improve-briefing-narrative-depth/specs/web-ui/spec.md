## ADDED Requirements

### Requirement: Rich briefing slide rendering
The system SHALL render deep briefing interpretation on presentation slides in a scannable format.

#### Scenario: Slide interpretation sections appear
- **WHEN** the Briefing presentation renders
- **THEN** each slide displays summary, meaning, risk, and action sections when those fields are present

#### Scenario: Evidence stays adjacent
- **WHEN** interpretation sections are displayed
- **THEN** concrete evidence and deep-dive references remain visible on the same slide

### Requirement: Narrative depth validation capture
The system SHALL capture validation output for the deeper briefing narrative on both validation codebases.

#### Scenario: Validation documents
- **WHEN** improve-briefing-narrative-depth implementation validation is complete
- **THEN** `docs/validation/briefing-narrative-depth-self.md` and `docs/validation/briefing-narrative-depth-civilsim.md` contain representative slide interpretation summaries

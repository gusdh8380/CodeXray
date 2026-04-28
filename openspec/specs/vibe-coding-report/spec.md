# vibe-coding-report Specification

## Purpose
The vibe-coding-report capability analyzes repository-local AI-agent and process artifacts, such as `AGENTS.md`, `CLAUDE.md`, `.claude/`, OpenSpec, `.omc/`, `.roboco/`, validation captures, handoff notes, and retrospectives, to produce an evidence-backed report about how the project was built. It feeds the web UI Vibe Coding tab with deterministic confidence, strengths, risks, next actions, and root-relative evidence paths, complementing source-quality capabilities by evaluating the agent collaboration environment rather than code structure alone.

## Requirements
### Requirement: Vibe-coding artifact detection
The system SHALL detect common vibe-coding and agent-environment artifacts in a target repository using deterministic local filesystem analysis.

#### Scenario: Agent instruction artifacts found
- **WHEN** a repository contains `CLAUDE.md`, `AGENTS.md`, `.claude/skills`, or `.claude/commands`
- **THEN** the vibe-coding report includes those paths as agent instruction evidence

#### Scenario: No vibe-coding artifacts found
- **WHEN** a repository contains none of the known vibe-coding artifacts
- **THEN** the vibe-coding report still returns successfully and marks the evidence confidence as low

### Requirement: Process area classification
The system SHALL classify detected artifacts into process areas for agent instructions, spec workflow, memory and handoff, validation, retrospectives, and automation.

#### Scenario: OpenSpec workflow artifacts found
- **WHEN** a repository contains `openspec/changes` or `openspec/specs`
- **THEN** the vibe-coding report classifies those paths under spec workflow evidence

#### Scenario: OMC memory artifacts found
- **WHEN** a repository contains `.omc/project-memory.json` or `.omc/sessions`
- **THEN** the vibe-coding report classifies those paths under memory and handoff evidence

#### Scenario: Validation artifacts found
- **WHEN** a repository contains `docs/validation`
- **THEN** the vibe-coding report classifies that path under validation evidence

### Requirement: Evidence-backed report
The system SHALL produce a structured report containing observed evidence, inferred strengths, inferred risks, and recommended next actions.

#### Scenario: Strong multi-area evidence
- **WHEN** a repository contains artifacts from at least three process areas
- **THEN** the vibe-coding report includes strengths and risks derived from those areas and cites the supporting evidence paths

#### Scenario: Missing validation evidence
- **WHEN** a repository contains agent instruction artifacts but no validation artifacts
- **THEN** the vibe-coding report includes a risk or next action about adding concrete validation captures

### Requirement: Confidence and interpretation boundary
The system SHALL report confidence and MUST distinguish observed facts from inferred interpretation.

#### Scenario: Evidence confidence is calculated
- **WHEN** the vibe-coding report is built
- **THEN** the result includes a confidence label based on the breadth of detected process areas

#### Scenario: Interpretation is evidence-linked
- **WHEN** the report includes a strength, risk, or next action
- **THEN** that item references at least one evidence path or explicitly states that evidence is missing

### Requirement: Deterministic serialization
The system SHALL serialize vibe-coding report data with `schema_version: 1`, deterministic ordering, and POSIX slash paths relative to the analyzed root.

#### Scenario: JSON schema marker
- **WHEN** the vibe-coding report is serialized as JSON
- **THEN** the output includes `schema_version: 1`

#### Scenario: Repeatable output
- **WHEN** the same repository is analyzed twice without file changes
- **THEN** the serialized vibe-coding report bytes are identical

### Requirement: Performance budget
The system SHALL complete deterministic vibe-coding report analysis within 5 seconds on the validation codebases.

#### Scenario: Self validation
- **WHEN** CodeXray repository path is analyzed
- **THEN** the vibe-coding report completes within 5 seconds and includes evidence for the current agent environment

#### Scenario: CivilSim validation
- **WHEN** CivilSim repository path is analyzed
- **THEN** the vibe-coding report completes within 5 seconds and returns a meaningful low, medium, or high confidence result

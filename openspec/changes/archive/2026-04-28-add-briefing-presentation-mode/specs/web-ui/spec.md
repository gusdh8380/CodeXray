## ADDED Requirements

### Requirement: Briefing presentation mode
The system SHALL render the Briefing tab as a presentation-mode experience inside the localhost web UI.

#### Scenario: Presentation controls appear
- **WHEN** the Briefing tab renders for a valid repository path
- **THEN** the fragment includes slide count, previous control, next control, and section navigation for the presentation slides

#### Scenario: Focused slide rendering
- **WHEN** the presentation-mode briefing first appears
- **THEN** the first slide is visible as the focused slide and non-focused slides are hidden or visually inactive

#### Scenario: Local slide navigation
- **WHEN** the user activates next, previous, or a section navigation control
- **THEN** the focused slide changes locally without requesting a new server analysis

#### Scenario: Keyboard navigation
- **WHEN** the presentation-mode briefing has focus and the user presses ArrowRight or ArrowLeft
- **THEN** the focused slide moves to the next or previous slide locally

### Requirement: Presenter-friendly briefing content
The system SHALL render presenter-friendly content for technical and non-technical audiences while keeping evidence visible.

#### Scenario: Presenter summary appears
- **WHEN** the Briefing tab renders
- **THEN** the fragment includes a concise presenter summary near the top of the presentation

#### Scenario: Evidence remains visible on slides
- **WHEN** a slide presents an interpretation
- **THEN** the slide displays concrete evidence such as grade, path, metric, hotspot, commit message, or process artifact near that interpretation

#### Scenario: Deep dive remains available
- **WHEN** a user reaches the final or deep-dive slide
- **THEN** the UI provides links or controls to inspect the existing detailed analyzer tabs

### Requirement: Briefing presentation validation capture
The system SHALL capture briefing presentation validation results for both validation codebases.

#### Scenario: Validation documents
- **WHEN** add-briefing-presentation-mode implementation validation is complete
- **THEN** `docs/validation/briefing-presentation-self.md` and `docs/validation/briefing-presentation-civilsim.md` contain representative presentation output summaries and navigation markers

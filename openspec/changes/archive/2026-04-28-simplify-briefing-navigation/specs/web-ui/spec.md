## MODIFIED Requirements

### Requirement: Briefing-first web navigation
The system SHALL organize the web UI around one top-level Briefing tab before low-level analyzer tabs, and SHALL keep briefing subsections inside the Briefing presentation controls instead of duplicating them as top-level tabs.

#### Scenario: Primary briefing tab appears
- **WHEN** the browser loads the web UI main page
- **THEN** the primary navigation includes exactly one top-level Briefing tab that requests `/api/briefing`

#### Scenario: Briefing subsections are not duplicate top-level tabs
- **WHEN** the browser loads the web UI main page
- **THEN** Architecture, Quality & Risk, How It Was Built, Explain, and Deep Dive are not rendered as separate top-level analysis tabs

#### Scenario: Detailed analyzers remain accessible
- **WHEN** the user reviews the top-level navigation
- **THEN** the UI still exposes the existing detailed analysis views for overview, inventory, graph, metrics, hotspots, quality, entrypoints, report, dashboard, vibe-coding evidence, and review

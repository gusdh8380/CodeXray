## Why

The Briefing tab now has presentation-mode navigation, but the slide content is still a thin repackaging of analyzer facts. The user intent is stronger: entering a local source/repository path should produce a developer-prepared, audience-ready analysis deck that explains what the repo is, its state, how it was made, and what the team should do next.

This change aligns with Vision.md's "understand + evaluate" core problem and non-developer vibe-coder / project-owner target user, plus Intent.md #5 (comprehensive report) and #6 (interactive dashboard).

## What Changes

- Deepen deterministic briefing narratives for each slide so they read like analysis, not metric labels.
- Add explicit interpretation fields: meaning, evidence, risk, and recommended action.
- Strengthen "How It Was Built" with git-history/process interpretation, not just commit counts.
- Improve non-developer explanation by translating graph/quality/hotspot signals into plain language.
- Keep every interpretation evidence-backed and deterministic.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `codebase-briefing`: Extend briefing slide content with deeper deterministic interpretation and action guidance.
- `web-ui`: Render the richer slide interpretation in the Briefing presentation.

## Impact

- Affected modules: `src/codexray/briefing/*`, `src/codexray/web/render.py`, `src/codexray/web/static/app.css`, tests, and validation docs.
- No external AI dependency and no new service dependency.
- Serialization remains `schema_version: 1` and deterministic.

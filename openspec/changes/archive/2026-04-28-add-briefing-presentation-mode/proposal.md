## Why

Users want to paste a local source/repository path and immediately get a deep but explainable repository analysis that feels like a developer-prepared presentation, not a stack of raw analyzer tabs. This change is aligned with Intent.md must-have #5 (one-page comprehensive report), #6 (interactive dashboard), and Vision.md target users including non-developer vibe-coders / project owners who need to explain what a codebase is, its status, and how it was built.

## What Changes

- Add a presentation mode to the Briefing experience with slide-like sections for audience-ready explanation.
- Keep the briefing evidence-rich: every slide-like section must cite concrete analyzer, path, grade, hotspot, or git-process evidence.
- Add local keyboard/navigation controls for moving between briefing sections without leaving the existing localhost web UI.
- Add a compact presenter summary that can be read aloud to a team or non-developer stakeholder.
- Preserve deep-dive access to existing analyzer tabs and raw evidence; this is not a replacement for the detailed analysis views.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `codebase-briefing`: Extend the briefing model contract to include presentation slides, presenter narrative, and audience-oriented evidence.
- `web-ui`: Render briefing presentation mode with local navigation controls while preserving the existing analyzer tabs and local-first constraints.

## Impact

- Affected modules: `src/codexray/briefing/*`, `src/codexray/web/render.py`, `src/codexray/web/static/app.css`, `src/codexray/web/templates/index.html`, and web/briefing tests.
- No new external service or SDK dependency.
- No breaking CLI or JSON schema change without `schema_version` preservation; any new briefing fields must be deterministic.

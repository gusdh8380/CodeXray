## Why

The web UI currently shows Briefing, Architecture, Quality & Risk, How It Was Built, Explain, and Deep Dive as separate top-level tabs, but each button reloads the same Briefing endpoint. This makes the navigation feel broken and conflicts with the new presentation-mode Briefing experience, where those sections already exist as internal slides.

This change aligns with Intent.md #6 (interactive dashboard) and the success criterion that the user can quickly decide what to do next: top-level navigation should expose distinct actions, while slide-level navigation should stay inside the Briefing view.

## What Changes

- Collapse the presentation section buttons into a single top-level `Briefing` tab.
- Keep Architecture, Quality & Risk, How It Was Built, Explain, and Deep Dive available inside the Briefing presentation controls.
- Update web UI tests so duplicate top-level `/api/briefing` tabs do not regress.
- Preserve all existing analyzer tabs and the `/api/briefing` endpoint.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `web-ui`: Change main navigation requirements so top-level tabs represent distinct analysis modes, with briefing subsections handled inside the Briefing presentation.

## Impact

- Affected files: `src/codexray/web/templates/index.html`, `tests/test_web_ui.py`, and `openspec/specs/web-ui/spec.md` after archive.
- No API or data model change.
- No new dependency.

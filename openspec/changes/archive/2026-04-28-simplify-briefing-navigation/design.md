## Context

The Briefing presentation mode now has its own slide controls and section dots. Keeping the same section names as top-level tabs creates duplicate controls with different behavior: the top-level tabs re-run `/api/briefing`, while the in-fragment controls move between slides locally.

## Goals / Non-Goals

**Goals:**

- Make the left navigation reflect distinct server-side analysis modes.
- Keep the Briefing presentation sections discoverable inside the Briefing result.
- Reduce visual height and cognitive load in the left nav.

**Non-Goals:**

- Redesigning the dashboard canvas in this change.
- Changing the `/api/briefing` endpoint contract.
- Removing any briefing slide content.

## Decisions

1. **Keep only one top-level Briefing tab.**
   - Rationale: top-level tabs should correspond to different analysis endpoints or distinct user actions.
   - Alternative considered: make the section tabs send a target slide parameter. Rejected because it adds state and still duplicates the slide dots.

2. **Use the existing presentation dots for section navigation.**
   - Rationale: they already move locally without re-analysis and match the deck mental model.

## Risks / Trade-offs

- **[Risk] Users may not see subsection names before opening Briefing.** → Mitigation: the first Briefing render includes slide dots, slide count, and section titles.

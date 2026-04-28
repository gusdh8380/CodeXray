## Context

The current Briefing tab already composes deterministic analyzers into Korean, presentation-like sections. However, the rendered experience is still a long document: useful, but not the same as opening a deck and walking teammates through "what this repo is, where it stands, how it was made, and what to do next." The target user now includes non-developer vibe-coders / project owners, so the UI needs a stronger audience-ready flow without hiding the underlying evidence.

## Goals / Non-Goals

**Goals:**

- Add deterministic slide-like briefing data derived from the existing briefing cards and analyzer evidence.
- Render the Briefing tab in a presentation mode with one focused section at a time, clear slide count, and local next/previous navigation.
- Include a presenter summary that can be read aloud to a teammate or non-developer stakeholder.
- Preserve evidence citations and deep-dive links so the briefing remains defensible, not shallow marketing copy.
- Keep the implementation local-first and build-pipeline-free.

**Non-Goals:**

- Exporting `.pptx` or PDF in this change.
- Replacing detailed analyzer tabs.
- Adding a new AI summarization dependency.
- Supporting remote sharing, collaboration, comments, or hosted presentations.

## Decisions

1. **Extend the deterministic briefing model instead of adding a separate deck builder.**
   - Rationale: the briefing model already has the correct inputs: inventory, quality, hotspots, summary, vibe-coding evidence, and git history.
   - Alternative considered: create a standalone `presentation` capability. Rejected because it would duplicate evidence collection and increase drift risk.

2. **Use HTML/CSS/vanilla JS for slide navigation inside the existing web UI.**
   - Rationale: the web UI intentionally avoids a JavaScript build pipeline. Simple section navigation can be done with existing assets.
   - Alternative considered: introduce a presentation framework. Rejected due to dependency weight and local-first simplicity.

3. **Keep every slide evidence-backed.**
   - Rationale: the product value is decision support. A slide that cannot cite a grade, path, metric, process artifact, or git event weakens trust.
   - Alternative considered: add pure narrative slides for readability. Rejected because the user explicitly wants deep analysis, not a thin summary.

4. **Make presentation mode the Briefing rendering, not a separate tab.**
   - Rationale: the primary path should be direct: enter path -> Briefing -> present. Extra tabs would make the main workflow less obvious.
   - Alternative considered: add a `Presentation` tab. Rejected for navigation sprawl.

## Risks / Trade-offs

- **[Risk] Slide UI could hide too much detail.** → Mitigation: each slide includes evidence chips/lists and deep-dive references remain visible.
- **[Risk] Browser-side navigation can become flaky.** → Mitigation: keep state local to the result fragment, add tests for rendered controls and no build step.
- **[Risk] Non-developer copy may become vague.** → Mitigation: build presenter notes from deterministic facts and require concrete evidence per slide.
- **[Risk] More briefing fields could break deterministic serialization.** → Mitigation: keep `schema_version: 1`, sorted output, and repeatability tests.

## Migration Plan

Existing `/api/briefing` continues to return an HTML fragment. The fragment becomes presentation-mode HTML, while the underlying analyzer tabs and current endpoint contract remain intact. If the change needs rollback, revert the briefing model field additions and render the previous sectioned document.

## Open Questions

- Whether a later change should add `.pptx` export using the presentation skill/plugin or a local document generator.
- Whether local Git URL / zip input should become the next primary workflow improvement after presentation mode.

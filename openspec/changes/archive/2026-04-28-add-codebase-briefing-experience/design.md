## Context

The current web UI exposes many analysis endpoints as peer tabs. That is useful for developers who already know what inventory, graph, metrics, hotspots, and entrypoints mean, but it does not match the emerging product intent: a user should provide a local repository and receive a presentation-like briefing that can be shown to teammates or non-developers.

Recent changes already moved toward this direction: deterministic strengths/weaknesses/next-actions summary is in flight, dynamic panel insights are in flight, and the committed vibe-coding report explains how a repo was built. This change should use those ideas while avoiding a broad rewrite or hidden dependency on AI.

## Goals / Non-Goals

**Goals:**
- Make the first web UI experience feel like a codebase analysis briefing deck.
- Preserve deep technical analysis for developers through a Deep Dive section.
- Provide non-developer explanations without removing quantitative evidence.
- Compose existing deterministic builders rather than duplicating analysis logic.
- Analyze git history as creation-process evidence, especially for vibe-coding workflows.
- Keep htmx + Jinja + static CSS; no frontend build pipeline.
- Continue using the ROBOCO/OpenSpec/OMC workflow and record decisions.

**Non-Goals:**
- No slide deck export in this change.
- No PDF/PPTX generation in this change.
- No AI-only narrative generation.
- No removal of existing low-level endpoints.
- No automatic code modification or refactoring.

## Decisions

1. **Add `src/codexray/briefing/` as a composition layer.**
   - It will call inventory, graph, metrics, entrypoints, quality, hotspots, summary, vibe-coding report, and git-history process builders.
   - It will produce frozen slotted dataclasses for sections such as executive, architecture, quality risk, build process, explain, and deep dive.
   - Rationale: the briefing is a product-level narrative model, not a new analyzer.

2. **Use deterministic rule-based copy for the first version.**
   - The non-developer explanation should be generated from observed facts: languages, file counts, grade, hotspot count, entrypoints, vibe confidence, commit timeline, and process artifacts added through history.
   - Rationale: local-first and trustworthy evidence matter more than fluent but unverifiable prose.

3. **Reframe navigation into high-level briefing sections.**
   - Primary sections: Briefing, Architecture, Quality & Risk, How It Was Built, Explain, Deep Dive.
   - Deep Dive exposes the existing Inventory, Graph, Metrics, Hotspots, Quality, Entrypoints, Report, Dashboard, Review, and Vibe Coding endpoints.
   - Rationale: this keeps depth while putting shareable narrative first.

4. **Keep existing endpoints compatible.**
   - Existing `/api/inventory` and similar endpoints remain available.
   - New briefing endpoints or tab routes add the new framing without breaking tests and external usage.

5. **Validate with self and CivilSim as briefing examples.**
   - The validation capture should show a representative briefing output: title/status, executive explanation, architecture highlights, risk highlights, build-process summary, non-developer talking points.

6. **Add git history analysis inside the briefing capability, not the existing hotspot git helper.**
   - Existing `hotspots.git_log` counts file changes for source files; briefing needs commit-level timeline and process evidence.
   - The first version will run bounded `git log` commands with a timeout and parse:
     - commit count and latest commits
     - commit type prefixes such as `feat`, `fix`, `docs`, `test`, `refactor`
     - OpenSpec/archive keywords and changed paths
     - validation, retro, handoff, AGENTS/CLAUDE/OMC/ROBOCO path additions or changes
     - evidence numbers in commit messages where present
   - Non-git directories return a graceful "history unavailable" result instead of failing.

## Risks / Trade-offs

- **Narrative becomes shallow** → Mitigation: every section links back to quantitative evidence and Deep Dive remains available.
- **UI gets cluttered** → Mitigation: primary navigation uses six high-level sections; detailed analyzers move into Deep Dive.
- **Existing in-flight changes overlap** → Mitigation: implement additively and do not revert summary/insights work.
- **Non-developer language overclaims** → Mitigation: use cautious copy such as "evidence suggests" and show confidence/evidence.
- **Performance regressions from composing many builders** → Mitigation: reuse existing builder order and keep validation under 5 seconds on self and CivilSim where possible.

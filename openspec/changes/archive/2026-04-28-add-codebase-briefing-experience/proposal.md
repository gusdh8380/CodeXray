## Why

Users do not primarily want a list of analysis tabs; they want to drop in a local repository and get a presentation-like briefing they can share with teammates or non-developers: what the repo is, what state it is in, how it was built, what risks matter, and what to do next. This change aligns with Vision.md's core problem ("understand + evaluate a codebase quickly"), Intent.md #5 (one-page report), Intent.md #6 (interactive dashboard), and the newly explicit non-developer vibe-coder / project-owner audience.

## What Changes

- Introduce a `codebase-briefing` capability that composes existing deterministic builders into a narrative briefing model.
- Add git-history based creation-process analysis focused on vibe-coding evidence: commit timeline, commit categories, OpenSpec/archive cadence, validation/retro/handoff additions, and whether commits show evidence-backed development.
- Reframe the web UI from a flat list of analysis tabs into presentation-like sections:
  - Briefing: executive summary, status, team-shareable explanation, top strengths/risks/actions.
  - Architecture: structure, entrypoints, dependency shape, key files.
  - Quality & Risk: grade, hotspots, weak dimensions, prioritized work.
  - How It Was Built: vibe-coding / agent-environment process report plus git-history creation timeline.
  - Explain: non-developer explanation and shareable talking points.
  - Deep Dive: existing raw analysis tabs for users who need depth.
- Keep deep analysis available; the new experience changes the primary navigation order and framing, not the underlying analyzers.
- Render the first screen as a briefing document rather than a tool landing page.
- Preserve local-first, deterministic behavior and no JavaScript build pipeline.

## Capabilities

### New Capabilities
- `codebase-briefing`: Compose inventory, graph, metrics, entrypoints, quality, hotspots, summary, vibe-coding report, and git-history creation-process evidence into a presentation-like briefing model.

### Modified Capabilities
- `web-ui`: Reframe the web UI navigation and result rendering around briefing sections while keeping deep-dive analysis available.

## Impact

- Affected code: new `src/codexray/briefing/` package, web routes/rendering/template/static CSS, and tests.
- Affected specs: new `codebase-briefing` spec and modified `web-ui` spec.
- Affected validation: self and CivilSim web/briefing captures.
- No external SaaS, direct SDK call, hosted service, or frontend build pipeline is introduced.
- Existing low-level endpoints can remain available for deep-dive compatibility.

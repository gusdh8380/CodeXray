## Why

Some repositories are not just code artifacts; they contain traces of the AI-assisted process that produced them, such as `CLAUDE.md`, `AGENTS.md`, `.claude/`, `.omc/`, `.roboco/`, OpenSpec changes, handoff notes, retrospectives, and validation captures. CodeXray should make those process signals legible so a non-developer vibe coder can understand whether the project was built with a reliable agent environment, what happened during creation, and what to improve next.

This change aligns with Intent.md must-have #3 (qualitative evaluation), #5 (decision-oriented report), and #6 (interactive dashboard). It also requires extending Vision.md target users to include non-developer vibe coders / AI-assisted project owners, because that audience is not currently explicit in the vision.

## What Changes

- Add a deterministic `vibe-coding-report` analysis capability that detects common vibe-coding artifacts and summarizes the repository's AI-assisted development process.
- Add a new web UI tab that renders the vibe-coding report as a readable Korean report for non-developer vibe coders.
- Classify detected evidence into process areas such as agent instructions, planning/spec workflow, memory/handoff, validation, automation, and review/retrospective.
- Provide strengths, risks, and next actions based on evidence, while clearly separating observed facts from inferred interpretation.
- Update Vision.md to include non-developer vibe coders / AI-assisted project owners as a target user group.
- Keep the first version deterministic and local-first; AI-generated interpretation can be a later opt-in enhancement.

## Capabilities

### New Capabilities
- `vibe-coding-report`: Detect vibe-coding process artifacts in a repository and produce a structured report with evidence, strengths, risks, and next actions.

### Modified Capabilities
- `web-ui`: Add a Vibe Coding tab and endpoint that renders the vibe-coding report in the existing localhost dashboard.

## Impact

- Affected code: new `src/codexray/vibe/` capability package, web routes/rendering/static styles, tests, and validation documents.
- Affected docs: `docs/vision.md` target users, OpenSpec specs, and validation captures for self and CivilSim.
- No external SaaS, server dependency, SDK integration, or build pipeline is introduced.
- No breaking CLI/API change is intended.

## Context

CodeXray currently evaluates source structure, quantitative quality, hotspots, reports, dashboards, and opt-in AI review. It does not evaluate the development process that produced a repository, even when the repository contains explicit AI-agent artifacts such as `CLAUDE.md`, `AGENTS.md`, `.claude/`, `.omc/`, `.roboco/`, OpenSpec changes, validation docs, retrospectives, or handoff notes.

The requested audience includes non-developer vibe coders. That extends the current Vision target users, so this change includes a small Vision update and keeps the report language decision-oriented rather than implementation-heavy.

This implementation itself must use the ROBOCO-initialized environment as first-class input: `.claude/skills/openspec-propose` / `/opsx:propose` for proposal creation, `.claude/skills/openspec-apply-change` for implementation workflow, `.omc/project-memory.json` for session memory, and `.roboco/config.json` for tool/environment expectations. The feature should make those same assets visible when analyzing this repository.

## Goals / Non-Goals

**Goals:**
- Detect common vibe-coding / agent-environment artifacts using deterministic local filesystem analysis.
- Produce a structured report with evidence-backed sections: environment, process timeline, strengths, risks, and next actions.
- Add a web UI tab that renders the report in readable Korean for non-developer vibe coders.
- Clearly distinguish observed facts from inferred interpretation.
- Preserve the existing local-first and no-build-pipeline web UI constraints.

**Non-Goals:**
- No automatic code modification or refactoring.
- No direct SDK calls or SaaS dependency.
- No claim that a repo was definitely vibe-coded from a single file; the report presents confidence and evidence.
- No AI-generated report text in the first version. AI interpretation can be a later explicit opt-in feature.
- No GitHub/Teams/Notion connector dependency.

## Decisions

1. **Introduce `src/codexray/vibe/` as a new deterministic capability.**
   - Rationale: The analysis target is process evidence, not source quality, so keeping it separate prevents web/report code from absorbing detection rules.
   - Alternative considered: fold the logic into `web/render.py`. Rejected because it would make the result hard to test and reuse.

2. **Use artifact classifiers with fixed weights and evidence paths.**
   - The builder will scan known files/directories and classify evidence into areas:
     - agent instructions: `CLAUDE.md`, `AGENTS.md`, `.claude/skills`, `.claude/commands`
     - spec workflow: `openspec/`, `openspec/changes`, `openspec/specs`
     - memory/handoff: `.omc/project-memory.json`, `docs/handoff*.md`
     - validation: `docs/validation/`, test/lint command references
     - retrospectives: `docs/vibe-coding/`, `retro*.md`
     - automation: `.roboco/`, `.husky/`, `.claude/settings*.json`, scripts/configs
   - Rationale: deterministic evidence makes the report inspectable and testable.
   - Alternative considered: use AI to infer the process from all markdown. Rejected for first version because constraints require trustworthy evidence and AI must be opt-in.

3. **Render for non-developers in the web UI, not as raw JSON first.**
   - The tab should lead with "what this means" and "next action" cards, then expose evidence tables.
   - Rationale: the target user may not know what `.omc/` or OpenSpec means.
   - Alternative considered: a developer-only artifact list. Rejected because it misses the user’s stated audience.

4. **Keep a confidence score, but avoid overclaiming authorship.**
   - The report can say "strong evidence of agent-assisted workflow" when multiple independent evidence areas exist.
   - It must say "no strong evidence found" when artifacts are absent.
   - Rationale: file names alone are signals, not proof of how all code was written.

5. **Update Vision.md in the same change.**
   - Rationale: "non-developer vibe coder" is a product audience change, not just a UI implementation detail.
   - Alternative considered: implement the tab without changing Vision. Rejected because AGENTS.md requires Intent/Vision drift to be handled explicitly.

## Risks / Trade-offs

- **False positives from template files** → Mitigation: report confidence and evidence categories, not binary truth.
- **False negatives for custom agent setups** → Mitigation: keep classifier rules easy to extend and show missing evidence as "not found", not "not used".
- **Overwhelming non-developer users** → Mitigation: start with summary cards and Korean plain-language explanations; put file-level evidence in secondary tables.
- **Performance on large repos** → Mitigation: follow Walk → Classify → Read discipline and read only small known docs/config files with size caps.
- **Spec overlap with existing AI review** → Mitigation: first version is deterministic process analysis; AI review remains separate and opt-in.
- **Agent-environment underuse while building this feature** → Mitigation: keep using `.claude` OpenSpec workflow, consult `.roboco/config.json` and `.omc/project-memory.json`, and record any new process decision before session end.

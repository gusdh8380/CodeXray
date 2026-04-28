## 1. Vision And Workflow Alignment

- [x] 1.1 Update `docs/vision.md` target users to include non-developer vibe coders / AI-assisted project owners.
- [x] 1.2 Reconfirm `.roboco/config.json`, `.omc/project-memory.json`, and `.claude` OpenSpec assets are reflected in the implementation rules.

## 2. Core Vibe-Coding Capability

- [x] 2.1 Create `src/codexray/vibe/{__init__,types,build,serialize}.py` using frozen slotted dataclasses.
- [x] 2.2 Implement deterministic artifact detection for agent instructions, spec workflow, memory/handoff, validation, retrospectives, and automation.
- [x] 2.3 Implement confidence, strengths, risks, and next actions with evidence paths and missing-evidence markers.
- [x] 2.4 Implement deterministic JSON serialization with `schema_version: 1` and root-relative POSIX paths.

## 3. Web UI Integration

- [x] 3.1 Add a Vibe Coding tab to the main web UI tab list.
- [x] 3.2 Add a `/api/vibe-coding` endpoint that validates paths and builds the vibe-coding report.
- [x] 3.3 Render the Vibe Coding tab as summary-first Korean HTML for non-developer vibe coders.
- [x] 3.4 Add CSS for readable summary cards and grouped evidence without introducing a build pipeline.

## 4. Tests

- [x] 4.1 Add unit tests for artifact detection and process area classification.
- [x] 4.2 Add unit tests for confidence, strengths, risks, next actions, and evidence boundary behavior.
- [x] 4.3 Add serializer tests for `schema_version: 1`, deterministic ordering, and POSIX paths.
- [x] 4.4 Add web UI tests for the tab, endpoint, Korean report rendering, and evidence grouping.

## 5. Validation Gates

- [x] 5.1 Run `openspec validate add-vibe-coding-report-tab --strict`.
- [x] 5.2 Run `uv run pytest -q`.
- [x] 5.3 Run `uv run ruff check`.
- [x] 5.4 Capture self validation in `docs/validation/vibe-coding-report-self.md` with meaningful output under 5 seconds.
- [x] 5.5 Capture CivilSim validation in `docs/validation/vibe-coding-report-civilsim.md` with meaningful output under 5 seconds.

## 6. Archive And Memory

- [x] 6.1 Archive the change after all validation gates pass.
- [x] 6.2 Fill any archived spec `## Purpose` placeholder immediately after archive.
- [x] 6.3 Record the new decision and learning in `.omc/project-memory.json`.

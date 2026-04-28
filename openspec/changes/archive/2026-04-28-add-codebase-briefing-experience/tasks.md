## 1. Briefing Model

- [x] 1.1 Create `src/codexray/briefing/{__init__,types,build,serialize}.py` with frozen slotted dataclasses.
- [x] 1.2 Compose existing inventory, graph, metrics, entrypoints, quality, hotspots, summary, and vibe-coding report builders into a briefing result.
- [x] 1.3 Add deterministic executive, architecture, quality-risk, build-process, explain, and deep-dive section content.
- [x] 1.4 Serialize briefing output with `schema_version: 1`, deterministic ordering, and POSIX paths.

## 2. Git History Creation Analysis

- [x] 2.1 Add bounded git-history collection for commit count, recent commits, type distribution, and changed path categories.
- [x] 2.2 Classify vibe-coding process commits for OpenSpec, validation, retrospectives, handoff, AGENTS/CLAUDE, `.claude`, `.omc`, and `.roboco`.
- [x] 2.3 Return graceful history-unavailable results for non-git paths or git timeout/failure.
- [x] 2.4 Integrate git-history creation evidence into the How It Was Built briefing section.

## 3. Web UI Reframe

- [x] 3.1 Add primary briefing navigation for Briefing, Architecture, Quality & Risk, How It Was Built, Explain, and Deep Dive.
- [x] 3.2 Add a briefing endpoint that validates paths and renders the full briefing.
- [x] 3.3 Render presentation-like Korean briefing sections with evidence cards and plain-language text.
- [x] 3.4 Keep existing detailed analyzer endpoints accessible through Deep Dive.
- [x] 3.5 Add CSS for deck-like briefing sections without introducing a frontend build pipeline.

## 4. Tests

- [x] 4.1 Add unit tests for briefing composition and deterministic serialization.
- [x] 4.2 Add unit tests for git-history parsing, commit type distribution, and vibe-coding process classification.
- [x] 4.3 Add tests for graceful history-unavailable behavior.
- [x] 4.4 Add web UI tests for primary briefing navigation, briefing endpoint, git-history build-process rendering, and Deep Dive access.

## 5. Validation Gates

- [x] 5.1 Run `openspec validate add-codebase-briefing-experience --strict`.
- [x] 5.2 Run `uv run pytest -q`.
- [x] 5.3 Run `uv run ruff check`.
- [x] 5.4 Capture self validation in `docs/validation/codebase-briefing-self.md` with meaningful briefing output under 5 seconds.
- [x] 5.5 Capture CivilSim validation in `docs/validation/codebase-briefing-civilsim.md` with meaningful briefing output under 5 seconds or graceful history-unavailable output.

## 6. Archive And Memory

- [x] 6.1 Archive the change after all validation gates pass.
- [x] 6.2 Fill any archived spec `## Purpose` placeholder immediately after archive.
- [x] 6.3 Record the briefing direction and git-history learning in `.omc/project-memory.json`.

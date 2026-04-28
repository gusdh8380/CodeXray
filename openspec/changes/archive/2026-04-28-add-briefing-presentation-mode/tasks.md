## 1. OpenSpec

- [x] 1.1 Validate `openspec validate add-briefing-presentation-mode --strict`

## 2. Briefing Model

- [x] 2.1 Add immutable presentation slide dataclasses to `src/codexray/briefing/types.py`
- [x] 2.2 Build deterministic slides and presenter summary in `build_codebase_briefing`
- [x] 2.3 Serialize presentation fields with `schema_version: 1` deterministic ordering
- [x] 2.4 Ensure each slide includes at least one concrete evidence item and deep-dive reference

## 3. Web UI Presentation Mode

- [x] 3.1 Render Briefing as a presentation-mode fragment with slide count and presenter summary
- [x] 3.2 Add previous/next/section controls with local vanilla JS navigation
- [x] 3.3 Add ArrowLeft/ArrowRight keyboard navigation scoped to the briefing fragment
- [x] 3.4 Style slide layout for readable desktop and mobile presentation use without adding a build pipeline
- [x] 3.5 Keep deep-dive controls for existing analyzer tabs visible from the final/deep-dive slide

## 4. Tests

- [x] 4.1 Add briefing model tests for slides, presenter summary, evidence presence, and deterministic serialization
- [x] 4.2 Add web UI tests for presentation controls, focused first slide, presenter summary, and deep-dive controls
- [x] 4.3 Add static asset tests or assertions for local navigation hooks
- [x] 4.4 Existing suite passes with `uv run pytest -q`

## 5. Validation

- [x] 5.1 `openspec validate add-briefing-presentation-mode --strict`
- [x] 5.2 `uv run pytest -q`
- [x] 5.3 `uv run ruff check`
- [x] 5.4 Self tree: Briefing presentation renders within 5 seconds and `docs/validation/briefing-presentation-self.md` is captured
- [x] 5.5 CivilSim tree: Briefing presentation renders within 5 seconds and `docs/validation/briefing-presentation-civilsim.md` is captured

## 6. Archive

- [x] 6.1 `openspec archive add-briefing-presentation-mode -y`
- [x] 6.2 Fill archived spec `## Purpose` placeholders if any are created
- [x] 6.3 Commit with concrete validation numbers

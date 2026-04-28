## 1. OpenSpec

- [x] 1.1 Validate `openspec validate improve-briefing-narrative-depth --strict`

## 2. Briefing Model

- [x] 2.1 Add slide interpretation fields to immutable briefing slide types
- [x] 2.2 Build deterministic summary/meaning/risk/action text for all six slides
- [x] 2.3 Add creation-story interpretation from git history and vibe-coding evidence
- [x] 2.4 Serialize new interpretation fields deterministically

## 3. Web Rendering

- [x] 3.1 Render slide interpretation sections in Briefing presentation
- [x] 3.2 Keep evidence and deep links visible on each slide
- [x] 3.3 Adjust CSS for readable compact slide sections

## 4. Tests

- [x] 4.1 Add briefing model tests for interpretation fields and creation-story fallback
- [x] 4.2 Add web UI tests for rendered summary/meaning/risk/action sections
- [x] 4.3 Existing suite passes with `uv run pytest -q`

## 5. Validation

- [x] 5.1 `openspec validate improve-briefing-narrative-depth --strict`
- [x] 5.2 `uv run pytest -q`
- [x] 5.3 `uv run ruff check`
- [x] 5.4 Self tree validation doc captured
- [x] 5.5 CivilSim validation doc captured

## 6. Archive

- [x] 6.1 `openspec archive improve-briefing-narrative-depth -y`
- [x] 6.2 Fill archived spec `## Purpose` placeholders if any are created
- [x] 6.3 Commit with concrete validation numbers

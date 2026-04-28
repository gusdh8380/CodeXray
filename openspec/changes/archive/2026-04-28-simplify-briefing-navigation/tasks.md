## 1. OpenSpec

- [x] 1.1 Validate `openspec validate simplify-briefing-navigation --strict`

## 2. Navigation Simplification

- [x] 2.1 Remove duplicate top-level Briefing subsection buttons from `index.html`
- [x] 2.2 Keep one top-level Briefing tab and all existing analyzer tabs
- [x] 2.3 Ensure subsection labels still render inside Briefing presentation controls

## 3. Tests

- [x] 3.1 Update main page test to assert exactly one top-level `/api/briefing` tab
- [x] 3.2 Add regression assertion that duplicate subsection labels are absent from top-level nav
- [x] 3.3 Existing suite passes with `uv run pytest -q`

## 4. Validation

- [x] 4.1 `openspec validate simplify-briefing-navigation --strict`
- [x] 4.2 `uv run pytest -q`
- [x] 4.3 `uv run ruff check`
- [x] 4.4 Capture a short validation note in `docs/validation/simplify-briefing-navigation.md`

## 5. Archive

- [x] 5.1 `openspec archive simplify-briefing-navigation -y`
- [x] 5.2 Fill archived spec `## Purpose` placeholders if any are created
- [x] 5.3 Commit with concrete validation result

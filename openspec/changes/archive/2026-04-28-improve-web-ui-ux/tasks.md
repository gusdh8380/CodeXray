## 1. OpenSpec

- [x] 1.1 Create `proposal.md`
- [x] 1.2 Create `design.md`
- [x] 1.3 Create `specs/web-ui/spec.md`
- [x] 1.4 Create `tasks.md`
- [x] 1.5 Validate `openspec validate improve-web-ui-ux`

## 2. UI Interaction

- [x] 2.1 Add status text and stable DOM hooks to the main template
- [x] 2.2 Auto-load Overview after app initialization
- [x] 2.3 Track active tab
- [x] 2.4 Add loading state for htmx requests
- [x] 2.5 Make Enter in path input rerun current tab
- [x] 2.6 Improve Review running fragment

## 3. Styling

- [x] 3.1 Style active tabs
- [x] 3.2 Style result-panel loading overlay
- [x] 3.3 Improve error and review running visual states
- [x] 3.4 Check responsive layout constraints

## 4. Tests

- [x] 4.1 Main page includes status text and auto-load hook
- [x] 4.2 Review running fragment includes polling feedback
- [x] 4.3 Existing web route tests still pass

## 5. Validation

- [x] 5.1 `openspec validate improve-web-ui-ux`
- [x] 5.2 `uv run pytest -q`
- [x] 5.3 `uv run ruff check`
- [x] 5.4 Restart local web UI and smoke `GET /`

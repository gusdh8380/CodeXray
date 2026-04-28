## 1. OpenSpec

- [x] 1.1 Create `proposal.md`
- [x] 1.2 Create `design.md`
- [x] 1.3 Create `specs/web-ui/spec.md`
- [x] 1.4 Create `tasks.md`
- [x] 1.5 Validate `openspec validate add-web-ui`

## 2. Dependencies

- [x] 2.1 Add `fastapi`, `uvicorn`, and `jinja2` to project dependencies
- [x] 2.2 Confirm `uv run pytest` can import FastAPI test client dependencies

## 3. Web Package Scaffold

- [x] 3.1 Add `src/codexray/web/__init__.py`
- [x] 3.2 Add `src/codexray/web/server.py`
- [x] 3.3 Add `src/codexray/web/routes.py`
- [x] 3.4 Add `src/codexray/web/render.py`
- [x] 3.5 Add Jinja templates and static assets

## 4. Analysis Routes

- [x] 4.1 Implement path validation helper
- [x] 4.2 Implement overview endpoint
- [x] 4.3 Implement inventory/graph/metrics/entrypoints/quality/hotspots endpoints
- [x] 4.4 Implement report endpoint
- [x] 4.5 Implement dashboard iframe endpoint
- [x] 4.6 Implement review opt-in endpoint
- [x] 4.7 Ensure errors return HTTP 400 fragments without stopping server

## 5. UI

- [x] 5.1 Build main page layout: path bar, recent paths, tabs, result panel
- [x] 5.2 Add htmx attributes for tab submissions
- [x] 5.3 Add localStorage recent path history capped at 5
- [x] 5.4 Add loading and error states
- [x] 5.5 Add AI review warning and explicit run control
- [x] 5.6 Add responsive desktop/mobile layout checks

## 6. CLI

- [x] 6.1 Add `codexray serve` command
- [x] 6.2 Add `--host`, `--port`, and `--no-browser` options
- [x] 6.3 Wire browser auto-open behavior

## 7. Tests

- [x] 7.1 Route smoke: `GET /`
- [x] 7.2 Path validation success/failure tests
- [x] 7.3 Endpoint smoke tests for deterministic routes
- [x] 7.4 Dashboard iframe fragment test
- [x] 7.5 Review endpoint opt-in marker test
- [x] 7.6 CLI option wiring test

## 8. Validation

- [x] 8.1 `openspec validate add-web-ui`
- [x] 8.2 `uv run pytest -q`
- [x] 8.3 `uv run ruff check`
- [x] 8.4 Capture `docs/validation/web-ui-self.md`
- [x] 8.5 Capture `docs/validation/web-ui-civilsim.md`
- [x] 8.6 Archive only after all gates pass

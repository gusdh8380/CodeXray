## 1. OpenSpec

- [x] 1.1 Create proposal/design/spec/tasks
- [x] 1.2 Validate `openspec validate improve-web-analysis-experience`

## 2. Readable Result Views

- [x] 2.1 Replace inventory JSON panel with summary + language table + raw details
- [x] 2.2 Replace graph JSON panel with graph summary + top connected files + raw details
- [x] 2.3 Replace metrics JSON panel with coupling summary + ranked table + raw details
- [x] 2.4 Replace hotspots JSON panel with category summary + priority table + raw details
- [x] 2.5 Replace quality JSON panel with grade cards + interpretation + raw details
- [x] 2.6 Replace entrypoints JSON panel with grouped entrypoint table + raw details
- [x] 2.7 Replace review JSON panel with readable review cards + raw details
- [x] 2.8 Improve report HTML rendering

## 3. Dashboard UX

- [x] 3.1 Make dashboard panel full-width within result area
- [x] 3.2 Increase iframe workspace height and remove cramped preview feel

## 4. Theme

- [x] 4.1 Add theme toggle control
- [x] 4.2 Add light/dark CSS variables
- [x] 4.3 Persist theme preference in localStorage

## 5. AI Cancel

- [x] 5.1 Add cancellable job state
- [x] 5.2 Add cancel route
- [x] 5.3 Add Cancel button to running fragment
- [x] 5.4 Add cancelled fragment

## 6. Tests

- [x] 6.1 Update web panel tests for readable result markers
- [x] 6.2 Add cancel route/status tests
- [x] 6.3 Add theme toggle DOM test
- [x] 6.4 Existing suite passes

## 7. Validation

- [x] 7.1 `openspec validate improve-web-analysis-experience`
- [x] 7.2 `uv run pytest -q`
- [x] 7.3 `uv run ruff check`
- [x] 7.4 Restart local web UI

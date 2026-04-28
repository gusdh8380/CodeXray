## 1. OpenSpec

- [x] 1.1 Create proposal/design/spec/tasks
- [x] 1.2 Validate `openspec validate add-dynamic-panel-insights --strict`

## 2. Insights core

- [x] 2.1 Add `src/codexray/web/insights.py` with prompt template (v1) and safety parser (3~5 bullets, 1+ risk, 1+ next-action, bullet length floor)
- [x] 2.2 Add disk cache helpers in `insights.py` (`~/.cache/codexray/insights/`, sha256 key over path|tab|raw_json_sha|adapter|prompt_version)
- [x] 2.3 Wire insights prompt to existing `ai/adapters.py` shell-out via `select_adapter()`

## 3. Background job

- [x] 3.1 Add `insights` job kind to `src/codexray/web/jobs.py`
- [x] 3.2 Add insights start route returning running fragment (cache hit returns ready immediately)
- [x] 3.3 Add insights status route returning ready / running / cancelled / failed / skipped fragments
- [x] 3.4 Add insights cancel route
- [x] 3.5 Add insights regenerate route (force cache miss)

## 4. Side panel UX

- [x] 4.1 Split right sidebar into senior (dynamic) and junior (static) panels in `templates/`
- [x] 4.2 Add "Generate insights" button + spinner + cancel + regenerate controls
- [x] 4.3 Refine static junior text to learning-context tone (메트릭 개념 중심) for 8 supported tabs
- [x] 4.4 Disable senior panel for Dashboard and Review tabs with sufficiency note

## 5. Tests

- [x] 5.1 Insights prompt parser tests (valid 3~5 bullets, missing risk, missing next-action, oversize, empty, bullet too short)
- [x] 5.2 Disk cache hit / miss / regenerate / prompt-version-bump tests
- [x] 5.3 Insights routes tests (start / status / cancel / regenerate)
- [x] 5.4 Senior+junior split DOM test in panel templates
- [x] 5.5 AI adapter unavailable fallback test
- [x] 5.6 Existing suite passes (`uv run pytest -q`)

## 6. Validation

- [x] 6.1 `openspec validate add-dynamic-panel-insights --strict`
- [x] 6.2 `uv run pytest -q`
- [x] 6.3 `uv run ruff check`
- [x] 6.4 Self tree: 8 탭 모두 인사이트 생성 + cache hit 확인 + `docs/validation/dynamic-panel-insights-self.md` 작성
- [x] 6.5 CivilSim tree: 같은 검증 + `docs/validation/dynamic-panel-insights-civilsim.md` 작성

## 7. Archive

- [x] 7.1 `openspec archive add-dynamic-panel-insights -y`
- [x] 7.2 Fill archived `web-ui` spec.md `## Purpose` if it regresses to TBD (per AGENTS.md step 10)
- [x] 7.3 `git commit -m "feat: ..."` (구체 수치 포함)

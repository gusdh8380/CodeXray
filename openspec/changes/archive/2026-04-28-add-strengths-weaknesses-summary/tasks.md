## 1. OpenSpec

- [x] 1.1 Create proposal/design/specs/tasks
- [x] 1.2 Validate `openspec validate add-strengths-weaknesses-summary --strict`

## 2. Summary core

- [x] 2.1 Create `src/codexray/summary/types.py` with `Strength`, `Weakness`, `Action`, `SummaryResult` frozen dataclasses (slots, evidence dict, schema_version)
- [x] 2.2 Create `src/codexray/summary/build.py` with `build_summary(quality, hotspots, metrics, entrypoints, inventory)` returning deterministic SummaryResult; implement strength rules (S1~S4), weakness rules (W1~W4), and action mapping dict
- [x] 2.3 Create `src/codexray/summary/serialize.py` with `to_json(result)` that emits schema_version=1, sorted keys, stable item ordering
- [x] 2.4 Create `src/codexray/summary/__init__.py` exporting public types and functions

## 3. Report integration

- [x] 3.1 Wire summary builder into `src/codexray/report/build.py` (reuse existing quality·hotspots·metrics inputs, no duplicate computation)
- [x] 3.2 Update Markdown writer (e.g. `src/codexray/report/markdown.py` or `to_markdown`) to render `## Strengths`, `## Weaknesses`, `## Next Actions` between Overall Grade and Top Hotspots; "(특이사항 없음)" fallback when items empty
- [x] 3.3 Keep `<!-- codexray-report-v1 -->` marker location unchanged

## 4. Web UI integration

- [x] 4.1 Update `src/codexray/web/render.py` `render_overview` to call summary builder and prepend three card sections; existing summary metrics remain below
- [x] 4.2 Update `render_report` to render the same three sections at the top of the readable HTML
- [x] 4.3 No new routes needed; verify existing `/api/overview` and `/api/report` continue to be deterministic and AI-free

## 5. Tests

- [x] 5.1 Add `tests/test_summary_rules.py` covering strength rules S1~S4, weakness rules W1~W4, action mapping (each weakness → expected action), Top 3 cap, empty fallback
- [x] 5.2 Add `tests/test_summary_serialize.py` covering schema_version, byte-equal determinism, stable item ordering
- [x] 5.3 Add `tests/test_report_strengths_weaknesses.py` covering Markdown section presence, ordering after Overall Grade and before Top Hotspots, evidence citation in items, byte determinism
- [x] 5.4 Extend `tests/test_web_ui.py` covering Overview tab three-card markers, Report tab three-section markers, AI-not-called assertion (monkeypatch select_adapter to raise; routes still succeed)
- [x] 5.5 `uv run pytest -q` — full suite passes (no regression on existing 268 tests)

## 6. Validation

- [x] 6.1 `openspec validate add-strengths-weaknesses-summary --strict`
- [x] 6.2 `uv run pytest -q`
- [x] 6.3 `uv run ruff check`
- [x] 6.4 Self tree (`/Users/jeonhyeono/Project/personal/CodeXray`): run `codexray report` + Web Overview + Web Report; capture results in `docs/validation/summary-self.md` (3 strengths, 3 weaknesses, 3 actions, evidence citations)
- [x] 6.5 CivilSim tree (`/Users/jeonhyeono/Project/personal/CivilSim`): same captures in `docs/validation/summary-civilsim.md`

## 7. Archive

- [x] 7.1 `openspec archive add-strengths-weaknesses-summary -y`
- [x] 7.2 Fill archived `summary` and `report`/`web-ui` spec.md `## Purpose` placeholders (per AGENTS.md step 10)
- [x] 7.3 `git commit -m "feat: add strengths/weaknesses/next-actions summary (Intent #5)"` with concrete numbers (e.g. "self: D(57) — strengths 3, weaknesses 3, actions 3")

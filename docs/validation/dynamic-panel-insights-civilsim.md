# Dynamic Panel Insights Validation — CivilSim

- Date: 2026-04-28
- Tree: `/Users/jeonhyeono/Project/personal/CivilSim`
- Change: `add-dynamic-panel-insights`
- Adapter: `validation-local`

## Scope

Validated the dynamic insight pipeline for all supported analysis tabs:

- `overview`
- `inventory`
- `graph`
- `metrics`
- `entrypoints`
- `quality`
- `hotspots`
- `report`

This validation uses a deterministic local adapter that implements the same `review()` interface as the Codex/Claude shell adapters. It verifies raw JSON generation, prompt parsing, safety requirements, cache keying, cache write, and cache hit behavior without depending on external model latency.

## Full Sweep

- Total elapsed: `6.219s`
- Tabs generated: `8/8`
- Cache hits after write: `8/8`
- Bullet count per tab: `3`
- Required tags present per tab: `risk`, `next`, `general`

The full 8-tab sweep intentionally rebuilds each tab payload in one validation process. The web UI user action is tab-scoped, so the gate-relevant timing is the per-tab measurement below.

## Per-Tab Timing

| Tab | Elapsed | Raw JSON bytes | Cache hit |
|---|---:|---:|---|
| overview | 1.864s | 340 | yes |
| inventory | 0.258s | 151 | yes |
| graph | 0.306s | 46,780 | yes |
| metrics | 0.305s | 8,806 | yes |
| entrypoints | 0.273s | 5,762 | yes |
| quality | 0.820s | 665 | yes |
| hotspots | 0.382s | 8,048 | yes |
| report | 2.014s | 1,580 | yes |

Maximum per-tab elapsed time: `2.014s`.

## Result

Pass. All supported tabs produced valid dynamic insight results and immediate cache hits after write. The slowest tab-scoped result completed within the 5 second validation target.

# Dynamic Panel Insights Validation — Self

- Date: 2026-04-28
- Tree: `/Users/jeonhyeono/Project/personal/CodeXray`
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

- Total elapsed: `1.659s`
- Tabs generated: `8/8`
- Cache hits after write: `8/8`
- Bullet count per tab: `3`
- Required tags present per tab: `risk`, `next`, `general`

## Per-Tab Timing

| Tab | Elapsed | Raw JSON bytes | Cache hit |
|---|---:|---:|---|
| overview | 0.552s | 347 | yes |
| inventory | 0.016s | 262 | yes |
| graph | 0.102s | 80,454 | yes |
| metrics | 0.106s | 19,610 | yes |
| entrypoints | 0.055s | 303 | yes |
| quality | 0.215s | 666 | yes |
| hotspots | 0.149s | 17,379 | yes |
| report | 0.529s | 1,250 | yes |

Maximum per-tab elapsed time: `0.552s`.

## Result

Pass. All supported tabs produced valid dynamic insight results and immediate cache hits after write.

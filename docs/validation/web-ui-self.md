# Web UI validation — CodeXray self

- Date: 2026-04-28
- Path: `/Users/jeonhyeono/Project/personal/CodeXray`
- Method: FastAPI `TestClient` endpoint smoke against `codexray.web.create_app()`
- Scope: deterministic endpoints plus AI review opt-in prompt. AI review execution intentionally not triggered.

| endpoint | status | seconds | marker | bytes | note |
| --- | ---: | ---: | --- | ---: | --- |
| `/api/overview` | 200 | 0.385 | yes | 616 | summary fragment |
| `/api/inventory` | 200 | 0.012 | yes | 581 | pretty JSON fragment |
| `/api/graph` | 200 | 0.068 | yes | 94927 | pretty JSON fragment |
| `/api/metrics` | 200 | 0.067 | yes | 23595 | pretty JSON fragment |
| `/api/entrypoints` | 200 | 0.033 | yes | 599 | pretty JSON fragment |
| `/api/quality` | 200 | 0.147 | yes | 1125 | pretty JSON fragment |
| `/api/hotspots` | 200 | 0.114 | yes | 20724 | pretty JSON fragment |
| `/api/report` | 200 | 0.371 | yes | 1558 | markdown readable fragment |
| `/api/dashboard` | 200 | 0.363 | yes | 153743 | iframe fragment, `codexray-dashboard-v1` present |
| `/api/review` | 200 | 0.001 | opt-in yes | 519 | prompt only |

Result: all deterministic endpoints returned meaningful HTTP 200 fragments within 5 seconds.

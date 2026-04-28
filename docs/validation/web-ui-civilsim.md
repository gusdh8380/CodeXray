# Web UI validation — CivilSim

- Date: 2026-04-28
- Path: `/Users/jeonhyeono/Project/personal/CivilSim`
- Method: FastAPI `TestClient` endpoint smoke against `codexray.web.create_app()`
- Scope: deterministic endpoints plus AI review opt-in prompt. AI review execution intentionally not triggered.

| endpoint | status | seconds | marker | bytes | note |
| --- | ---: | ---: | --- | ---: | --- |
| `/api/overview` | 200 | 1.949 | yes | 627 | summary fragment |
| `/api/inventory` | 200 | 0.257 | yes | 377 | pretty JSON fragment |
| `/api/graph` | 200 | 0.308 | yes | 67006 | pretty JSON fragment |
| `/api/metrics` | 200 | 0.311 | yes | 12724 | pretty JSON fragment |
| `/api/entrypoints` | 200 | 0.278 | yes | 8628 | pretty JSON fragment |
| `/api/quality` | 200 | 0.829 | yes | 1123 | pretty JSON fragment |
| `/api/hotspots` | 200 | 0.378 | yes | 11448 | pretty JSON fragment |
| `/api/report` | 200 | 2.062 | yes | 1741 | markdown readable fragment |
| `/api/dashboard` | 200 | 2.066 | yes | 113532 | iframe fragment, `codexray-dashboard-v1` present |
| `/api/review` | 200 | 0.001 | opt-in yes | 519 | prompt only |

Result: all deterministic endpoints returned meaningful HTTP 200 fragments within 5 seconds.

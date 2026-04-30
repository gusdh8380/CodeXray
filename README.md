# CodeXray

> 임의의 코드베이스를 입력하면 구조를 시각화하고 품질을 평가해, **"다음에 무엇을 할지"의 근거**를 제공한다.

8개 CLI 명령으로 인벤토리·의존성 그래프·메트릭·진입점·정량 등급·핫스팟·종합 리포트·인터랙티브 대시보드·AI 정성 평가를 한 번에. 결정론적 정량 분석이 우선, AI는 그 위에 정성 권고만 더한다.

## Quickstart

```bash
git clone https://github.com/gusdh8380/CodeXray.git
cd CodeXray
uv sync

# 가장 의미 있는 한 줄 — 인터랙티브 대시보드
uv run codexray dashboard /path/to/your/repo > dashboard.html
open dashboard.html
```

## 8개 명령

| 명령 | 출력 | 비용 |
|---|---|---|
| `codexray inventory <path>` | 언어·파일·LoC 표 | 0.5s |
| `codexray graph <path>` | 의존성 그래프 JSON (Py/JS/TS/C# type-resolved) | 0.6s |
| `codexray metrics <path>` | fan-in/out · SCC · is_dag JSON | 0.5s |
| `codexray entrypoints <path>` | 진입점 식별 JSON (`__main__`, `Main`, MonoBehaviour, manifests) | 0.5s |
| `codexray quality <path>` | 4차원(coupling/cohesion/documentation/test) A~F 등급 JSON | 1.0s |
| `codexray hotspots <path>` | 변경빈도×결합도 4 카테고리 매트릭스 JSON | 0.7s |
| `codexray report <path>` | 1페이지 종합 Markdown + 룰 기반 권고 5개 | 2.4s |
| `codexray dashboard <path>` | self-contained HTML 인터랙티브 대시보드 | 2.4s |
| `codexray review <path>` | AI 정성 평가 JSON (codex/claude CLI 셸아웃) | 1~5분 |

대상 언어: **Python · JavaScript · TypeScript · C#** (Java는 후속).

## 예시 출력 (Unity C# 게임 검증)

```text
$ codexray report ~/CivilSim
# CodeXray Report — `~/CivilSim`
**Date:** 2026-04-28

## Overall Grade: D (40)
| dimension | grade | score | detail |
| coupling | F | 33 | avg_fan_inout=6.72, max=44 |
| cohesion | A | 92 | groups_evaluated=3 |
| documentation | F | 33 | documented=86, items_total=262 |
| test | F | 4 | ratio=0.02, src_loc=8684, test_loc=194 |

## Top Hotspots
| path | change_count | coupling |
| `Assets/Scripts/Core/GameManager.cs` | 15 | 45 |
| `Assets/Scripts/Core/GameEvents.cs`  | 11 | 25 |
...

## Recommendations
1. Top hotspot: `Core/GameManager.cs` (change=15, coupling=45). 책임 분리·테스트 추가 우선.
2. `coupling` grade F (score 33). detail: avg_fan_inout=6.72, max=44.
3. `test` grade F (score 4). detail: ratio=0.02.
4. Cycle detected — largest SCC size 14, 39 SCCs total. 사이클 분해 검토.
...
```

AI 정성 평가는 본인 구독을 셸아웃으로 호출 (별도 API 키 결제 불필요):

```text
$ CODEXRAY_AI_TOP_N=1 codexray review ~/CivilSim
{
  "backend": "codex",
  "reviews": [{
    "path": "Assets/Scripts/Core/GameManager.cs",
    "dimensions": {
      "design": {"score": 57, "evidence_lines": [16, 19, 21, 60, 102, 122],
        "comment": "싱글턴 + 다수 서브시스템 직접 노출은 서비스 로케이터 형태...",
        "suggestion": "도메인별 파사드(예: 건설/인구/인프라)로 분리하고 ..."},
      ...
    },
    "confidence": "medium",
    "limitations": "..."
  }]
}
```

## 환경변수

| 이름 | 기본값 | 설명 |
|---|---|---|
| `CODEXRAY_AI_BACKEND` | `auto` | `auto` (codex > claude 자동 감지) / `codex` / `claude` 강제 |
| `CODEXRAY_AI_TOP_N` | `5` | `review` 명령이 처리할 hotspot 파일 수 |

## AI 백엔드 (선택)

`review` 명령은 다음 중 하나만 있으면 됩니다:
- **OpenAI Codex CLI** — `brew install --cask codex && codex login` (ChatGPT Plus/Pro/Codex Plus 구독 활용)
- **Claude Code** — `claude` CLI가 PATH에 있으면 자동 사용 (Claude Pro/Max 구독 활용)

API 키 별도 결제 없이 본인 구독 한도 안에서 호출. 어느 도구가 깔려 있든 동일 인터페이스(`AIAdapter` Protocol).

## 아키텍처

```
src/codexray/
├── walk.py            ← .gitignore + 무시 디렉토리 + 심볼릭 링크 비추적
├── language.py        ← 확장자 → 언어 매핑
├── loc.py             ← 비어있지 않은 줄 수
├── inventory.py       ← 언어별 파일·LoC·mtime 집계
├── render.py          ← rich.table 인벤토리 출력
├── graph/             ← 파일↔파일 의존성 (Python AST + JS 정규식 + C# type-resolution)
├── metrics/           ← fan-in/out + Tarjan SCC + is_dag
├── entrypoints/       ← __main__ / Main / MonoBehaviour / manifest detector
├── quality/           ← 4차원 점수 + A~F 매핑
├── hotspots/          ← git log + 결합도 매트릭스
├── report/            ← 6 builder 종합 + 룰 기반 권고 + Markdown
├── dashboard/         ← 6 builder 종합 + 단일 HTML + D3 force-directed
├── ai/                ← 어댑터 패턴 (Codex/Claude CLI 셸아웃) + 안전장치 강제 파서
└── cli.py             ← typer 진입점 (8 서브커맨드)
```

`graph` → `metrics`/`hotspots`/`report`/`dashboard`의 입력이고, `hotspots` → `review`의 우선순위 입력. 모든 하위 모듈은 결정론적 + frozen dataclass.

## 개발

```bash
uv sync
uv run pytest -q          # 295 tests
uv run ruff check
uv run codexray report .  # 자기 자신에게 적용 (현재 D(57))
```

### Web UI (React SPA)

`uv run codexray serve` 가 띄우는 웹 UI는 React + Vite + Tailwind v4. 백엔드 변경 후 정적 자산만 다시 빌드하면 됨:

```bash
cd frontend
npm install        # 최초 1회
npm run build      # frontend/dist 생성 → FastAPI가 정적 서빙
```

`frontend/dist`가 없으면 `/` 라우트는 SPA를 제공하지 않으므로 빌드를 한 번은 실행해야 한다. 개발 중 핫리로드가 필요하면 별도 터미널에서 `npm run dev` (Vite dev server, 백엔드 API는 8080으로 프록시).

## 프로젝트 규약

`docs/`에 vision/intent/constraints + vibe-coding 5단계 + 검증 메모 + 회고. `openspec/`에 12개 archived change(매 변경의 proposal/design/spec/tasks). 모든 변경은 OpenSpec validate 게이트 통과 + CodeXray 자기 + CivilSim 두 트리에서 5초 내 의미 있는 결과 게이트 통과.

설계 원칙은 `docs/constraints.md`에 명시 — **로컬 실행 우선, AI는 opt-in, 근거 라인 인용 필수, 사용자가 거절·재평가 가능**.

## Status

**MVP 1차 출하 완료** (2026-04-28). intent.md의 6개 핵심 feature 모두 동작. 후속 변경 후보:

- `add-report-with-review` — Markdown 리포트에 AI 권고 통합
- `add-dashboard-review-overlay` — 대시보드에 AI 리뷰 패널
- `add-quality-complexity` — cyclomatic 복잡도 차원 추가
- `add-graph-pipeline-cache` — graph 빌드 공유로 dashboard·report 가속
- `add-graph-java` — Java import 추출

회고: [`docs/vibe-coding/retro-2026-04-28.md`](docs/vibe-coding/retro-2026-04-28.md)

## License

MIT.

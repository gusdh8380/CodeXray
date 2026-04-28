# CodeXray — Agent Conventions

이 문서는 Codex CLI / Claude Code / 기타 코딩 에이전트가 이 프로젝트에 진입할 때 가장 먼저 읽어야 할 핸드북입니다. 어느 모델로 작업하든 같은 워크플로를 유지하기 위함입니다.

## 한 줄 정의

코드베이스 입력 → 구조 분석 + 정량 등급 + AI 정성 평가 + 시각화 → 사용자가 "다음 행동"을 결정할 근거를 제공하는 1인 도구.

세부 비전·의도·제약은:
- `docs/vision.md`
- `docs/intent.md`
- `docs/constraints.md`
- `docs/vibe-coding/retro-2026-04-28.md` (MVP 출하 회고)

## 현재 상태 (2026-04-28)

- **MVP 6개 feature 모두 출하 완료** — 12 changes / 14 commits
- **8 CLI 명령**: `inventory`, `graph`, `metrics`, `entrypoints`, `quality`, `hotspots`, `report`, `dashboard`, `review`
- **233 tests passing**, **ruff clean**
- **검증 자료**: `docs/validation/` 아래 self + CivilSim 결과 영구 보관
- **다음 변경**: `add-web-ui` (CLI를 웹 UI로 제어) — 명세 미시작
- 진행 중 결정·열린 질문은 `docs/handoff-to-codex.md` 참고

## Tech stack

- Python 3.11+
- uv (가상환경 + 의존성)
- typer (CLI)
- rich (테이블 출력)
- pathspec (gitignore)
- pytest + ruff
- D3 v7 (대시보드, CDN)
- AI 호출: codex / claude CLI 셸아웃 어댑터 (직접 SDK 호출 X)

## 워크플로 — OpenSpec 4박자

이 프로젝트는 **OpenSpec change cycle**을 엄격히 따릅니다. **새 기능은 코드 전에 4개 artifact 작성·검증 후 구현**.

```
1. openspec new change <kebab-name> --description "..."
2. proposal.md  ← Why / What changes / Capabilities (new + modified) / Impact
3. design.md    ← Goals / Non-Goals / Decisions (대안 + 근거) / Risks / Open Questions
4. specs/<capability>/spec.md
   - ## ADDED Requirements / ## MODIFIED Requirements
   - ### Requirement: <name>  +  SHALL/MUST/MUST NOT 본문
   - #### Scenario: <name>  +  WHEN/THEN  (정확히 4 hashtags)
   - 모든 Requirement는 1+ Scenario 필수
   - MODIFIED는 기존 Requirement 블록 전체 복사 후 수정
5. tasks.md     ← - [ ] 1.1 ... 체크박스 (apply 단계가 파싱)
6. openspec validate <name>   ← 통과해야 구현 시작
7. 구현 + tasks.md 체크오프
8. 검증 (아래 4 게이트)
9. openspec archive <name> -y  ← delta spec을 main spec으로 동기화
10. archive된 `openspec/specs/<capability>/spec.md`의 `## Purpose`가 `TBD - created by archiving change ...` placeholder면 한 단락으로 채우기 (capability 한 줄 정의 + CLI 명령 + 다른 capability와의 입출력 관계)
11. git commit -m "feat: ..." (구체 수치 포함, 예: "CivilSim D(40), top hotspot GameManager.cs(15×45)")
```

### 4개 게이트 (모두 통과해야 archive·commit)

1. `openspec validate <change>` 통과
2. `uv run pytest -q` 모두 통과 (회귀 0)
3. `uv run ruff check` clean
4. **자기 + CivilSim 두 트리에서 5초 내 의미 있는 결과** — `docs/validation/<feature>-{self,civilsim}.md`로 캡처

게이트 1개라도 실패하면 archive 금지. 명세 단계 건너뛰기 금지 — artifact 작성이 곧 작업의 일부.

## 검증 디시플린

매 변경마다 두 트리에서 측정:

| 트리 | 경로 | 특성 |
|---|---|---|
| **자기 적용** | `.` (`/Users/jeonhyeono/Project/personal/CodeXray`) | 자기 도구로 자기 측정 — self-validation |
| **사용자 자산** | `/Users/jeonhyeono/Project/personal/CivilSim` | Unity C# 게임, 50k 파일 트리, type-resolution C# 검증 게이트 |

추상 검증("일반적인 코드베이스") X. 두 구체 트리에서 결과를 capture하고 `docs/validation/{feature}-{self|civilsim}.md`로 저장.

CivilSim 현재 측정값(반복 비교 기준): nodes 53 · internal edges 178 · coupling avg 6.72 · grade D(40) · 1순위 hotspot `Assets/Scripts/Core/GameManager.cs (15×45)`.

## 코드 컨벤션

- **모든 데이터클래스**: `@dataclass(frozen=True, slots=True)` (immutable + 메모리 효율)
- **JSON 스키마 출력**: 모두 `schema_version: 1` 포함, 결정론적 정렬
- **Stdout for data, stderr for warnings/info** — 사용자가 `>` 리다이렉트 자유
- **프로그램 종료 코드**: 정상 0, 검증 실패 2
- **Path는 항상 POSIX 슬래시 + 입력 루트 기준 상대경로** (그래프·hotspot·report 모두)
- **결정론**: 같은 입력 → 같은 stdout 바이트 (test에 회귀 검사 의무)
- **Walk → Classify → Read 순서** (Read를 먼저 하면 비-소스 파일까지 읽어 성능 박살 — `entrypoints`에서 한 번 발생, 0.45s로 회복)
- **새 capability 디렉토리**: `src/codexray/<name>/{__init__,types,build,serialize}.py` 패턴 일관 (graph, metrics, entrypoints, quality, hotspots, report, dashboard, ai 모두 동일 구조)

## AI 통합 — 어댑터 패턴

직접 SDK 호출 금지. `src/codexray/ai/adapters.py`의 `AIAdapter` Protocol 따라 셸아웃:

- `CodexCLIAdapter` — `codex exec --color never --skip-git-repo-check --ephemeral --output-last-message <tmp>`
- `ClaudeCLIAdapter` — `claude -p <prompt>`
- `select_adapter(env)` — `CODEXRAY_AI_BACKEND={auto,codex,claude}`, default `auto` 우선순위 codex > claude

**안전장치는 명세에 강제** (constraints.md Top risk: "AI 평가 부정확 → 잘못된 의사결정"):
- 빈 `evidence_lines` → skipped 격리
- 라인 번호 파일 범위 초과 → skipped 격리
- 빈 `comment`/`suggestion`/`limitations` → skipped 격리
- 잘못된 `confidence` (low/medium/high 외) → skipped 격리

새 AI feature 추가 시 같은 안전장치 패턴 따를 것.

## 코드 구조

```
src/codexray/
├── walk.py            ← .gitignore + 무시 디렉토리 + 심볼릭 링크 비추적
├── language.py        ← 확장자 → 언어 매핑 (Python/JS/TS/Java/C#)
├── loc.py             ← 비어있지 않은 줄 수
├── inventory.py       ← 언어별 파일·LoC·mtime 집계
├── render.py          ← rich.table 인벤토리 출력
├── graph/             ← 파일↔파일 의존성 (Python AST + JS 정규식 + C# type-resolution)
├── metrics/           ← fan-in/out + Tarjan SCC + is_dag
├── entrypoints/       ← __main__ / Main / MonoBehaviour / pyproject·package.json
├── quality/           ← 4차원(coupling/cohesion/documentation/test) A~F 매핑
├── hotspots/          ← git log + 결합도 매트릭스 4 카테고리
├── report/            ← 6 builder 종합 + 룰 기반 권고 + Markdown
├── dashboard/         ← 6 builder 종합 + 단일 HTML + D3 force-directed
├── ai/                ← 어댑터 패턴 (Codex/Claude CLI 셸아웃) + 안전장치 강제 파서
└── cli.py             ← typer 진입점 (8 서브커맨드)
```

`graph` → `metrics`/`hotspots`/`report`/`dashboard`의 입력. `hotspots` → `review`의 우선순위 입력.

## 환경

- macOS Darwin / arm64
- Git: `~/Project/personal/`은 gusdh8380(personal) 계정 — `~/.gitconfig.personal`에 includeIf 설정됨
- SSH: `github-personal` / `github-work` alias로 다중 계정 라우팅
- gh CLI: 두 계정 모두 로그인 가능, `gh auth switch -u <name>`으로 전환
- Codex CLI: `/opt/homebrew/bin/codex` v0.125+ — `codex login`으로 ChatGPT Plus / Codex Plus 인증
- Claude Code: `/opt/homebrew/bin/claude` v2.1+ — Pro/Max 구독으로 인증

## 회피할 안티 패턴

- **여러 capability를 한 변경에 묶기** — 각자 분리된 변경
- **명세 단계 건너뛰기** — artifact 작성이 곧 작업
- **자기 적용 안 하는 도구** — 자기 검증이 최강 evidence
- **AI 의존 우선** — 결정론적 정량 분석이 먼저, AI는 그 위에 정성만
- **하드코딩 임계치** — design.md에 명시 + 후속 조정 가능
- **외부 SaaS·서버 의존** — 로컬 실행만 (constraints.md)
- **빌드 파이프라인** — 1차 단추는 가능한 한 vanilla (지금 dashboard도 단일 HTML + D3 CDN)

## 다음 변경

`docs/handoff-to-codex.md` 참고. 마지막 미결정 항목과 추천이 거기 정리돼 있습니다.

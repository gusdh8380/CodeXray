# Vibe Coding Retro — 2026-04-29 Intent Drift & ROBOCO Underuse

이전 retro(2026-04-28)는 빈 폴더 → MVP 6 feature 출하의 회고였다. 이 retro는 *그 환경 위에서 후속 세션이 어떻게 어긋났는가*의 회고다.

## 한 줄 요약

ROBOCO init이 만든 vibe-coding 풀 환경 중 **OpenSpec만 잡고 나머지를 수작업으로 대체**하는 바람에, Intent에 이미 있던 핵심 기능(강점/약점 Top 3)을 빼먹고 후순위 기능(시니어/주니어 sidebar)을 먼저 만들었다. 사용자가 "Intent.md 무시했다"·"ROBOCO init한 이유 없다"고 정확히 짚었다.

## 무엇을 했나 (이번 세션)

- archive된 10 capability spec의 `## Purpose` placeholder 일괄 채움 + AGENTS.md 워크플로 step 10 추가 → 1 commit (7297bf8)
- `add-dynamic-panel-insights` 명세 작성·구현·자동 검증 (시니어/주니어 sidebar 분리, AI 동적 인사이트, 디스크 캐시) → 268 tests passed, 검증 게이트 4(자기/CivilSim) 미완 상태로 정지
- 사용자가 "전반적 가독성 부족", "Intent.md 무시", "ROBOCO init이 만든 환경 미활용"을 짚어 작업 보류 + 회고 진입

## ROBOCO init이 만든 자산 vs 실제 활용

| 자산 | 활용 |
|---|---|
| `openspec/` 4박자 환경 | ✅ |
| `docs/{vision,intent,constraints}.md` | ⚠️ MVP 기간엔 따랐지만 이번 세션엔 사용자 지적 후에야 read |
| `AGENTS.md` | ⚠️ 일부만, "vibe-coding 5단계"의 Intent 재확인 단계 누락 |
| `INTENT.md` (root, 한 페이지 인덱스) | ❌ 존재 자체를 인지 못함 |
| `.claude/commands/opsx` 슬래시 명령 | ❌ |
| `.claude/skills/openspec-{propose,explore,apply,archive}` | ❌ — 수동으로 4 artifact 작성 |
| `.omc/project-memory.json` | ❌ |
| `.omc/sessions`, `.omc/state` | ❌ |
| `.roboco/config.json` `interview.tools` | ❌ githubMcp/omc 무시 |
| `.husky/pre-commit` | ⚠️ placeholder("No lint configured") 확인 안 함 |

요약: ROBOCO init은 vibe-coding *풀 환경*을 구축했지만 후속 세션은 OpenSpec만 잡고 나머지를 수작업으로 대체. 환경의 가속·정합 효과 미발휘.

## Root Cause

1. **세션 시작 시 환경 inventory 절차 부재** — `.claude/`·`.omc/`·`.roboco/` 디렉토리를 한 번도 listing하지 않고 곧장 OpenSpec 진입.
2. **상위 메타 문서를 늦게 또는 안 읽음** — `INTENT.md`(root)는 환경의 *입구*인데 미인지. `docs/intent.md`도 사용자 지적 후 read.
3. **자동화 도구 미인지** — `openspec-{propose,apply-change,archive-change}` skill, `/opsx:propose` 슬래시 명령이 있는데 수동 명세 작성.
4. **OMC 프로젝트 메모리 미활용** — `.omc/project-memory.json`에 결정·학습 누적 안 함. CLAUDE.md global의 OMC 디시플린이 적용 안 됨.

## 결과적 비용

- **사용자 표명 → Intent 매핑 단계 누락** — "Overview에 잘한 점/아쉬운 점" 표명이 사실 Intent.md 5번 "강점/약점 Top 3"였다. Intent를 봤다면 인터뷰 round를 줄이고 곧장 정렬된 변경에 들어갈 수 있었음.
- **시니어/주니어 패널 변경의 Intent 정합도** — constraints 정신엔 부합하지만 Intent 5번을 채우지 않음. 우선순위가 후순위였어야 함.
- **수동 명세 작성 시간** — `/opsx:propose` 호출했으면 더 짧았을 작업이 사람-LLM 인터뷰로 확장됨.

## 즉시 적용 교정

### 1. 세션 시작 시 환경 inventory 의무화
- `ls -la` + `.claude/{commands,skills}` + `.omc/` listing
- `INTENT.md` (root) + `AGENTS.md` + `docs/{vision,intent,constraints}.md` + `.omc/project-memory.json` 일괄 read

### 2. 사용자 표명 → Intent 매핑 명시화
사용자가 새 의도 표명 시 Intent.md / Vision.md의 어느 항목과 매핑되는지 명시적으로 짚는다. 매핑 불가하면 Intent/Vision 자체 변경을 별도 결정으로 분리한다.

### 3. 자동화 도구 우선 호출
- 새 변경 작성: `.claude/skills/openspec-propose` 또는 `/opsx:propose` 슬래시 명령
- 적용·archive도 같은 패턴 (`openspec-apply-change`, `openspec-archive-change`)

### 4. OMC 프로젝트 메모리 활용 사이클
- 세션 시작 시 `.omc/project-memory.json` read로 이전 세션 결정 인지
- 새 결정·학습은 거기에 누적

## 프로세스 변경 (이 retro와 함께 commit)

- **AGENTS.md** — `## 매 세션 시작 절차 (Step 0/1/2/3)` 섹션 신규 추가, OpenSpec 4박자 *진입 전* 의무화.
- **vibe-start skill** (`~/.claude/skills/vibe-start/SKILL.md`) —
  - Phase 4 `INTENT.md` 템플릿에 "Next session entry" 섹션 의무 포함
  - Phase 8.5 신규 — 다음 세션 시작 프롬프트 템플릿 출력

## 다음 vibe 프로젝트로 가져갈 것

1. **환경 셋업 후 "다음 세션 시작 가이드"를 INTENT.md에 박기** — 환경의 *입구*가 한 페이지에 모이게.
2. **vibe-coding 5단계의 Step 1(Intent)은 *매 세션 첫 메시지*에서 재실행** — 한 번 작성하고 끝나지 않음. 매 세션 reread.
3. **roboco init이 만든 자산 inventory 체크리스트를 INTENT.md에 박기** — 다음 세션이 곧장 활용 가능하도록.
4. **사용자 표명 → Intent 매핑 단계를 워크플로에 강제** — 새 변경 명세 진입 *전* "이 표명은 Intent의 X 항목과 정렬"이라는 한 줄을 proposal.md `## Why`에 의무 포함.

## 메타: 이 회고 자체

이전 retro(2026-04-28)는 *MVP 출하* 회고. 이 retro는 *후속 세션의 환경 미활용*이라는 다른 패턴. 두 종류 retro가 docs/vibe-coding/에 모이면 다음 vibe 프로젝트가 두 패턴 모두를 처음부터 회피 가능.

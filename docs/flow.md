# CodeXray 동작 흐름

> 마지막 갱신: 2026-05-01

레포 경로 하나 입력 → 5섹션 브리핑 + 9개 미시 분석 탭 + 그래프 시각화 + 바이브코딩 진단까지의 전체 흐름.

## 5 단계 개요

```
[1] 결정론 분석     → 코드 트리 자체에서 사실 수집 (Python만, AI 없음, ~5초)
       ↓
[2] 번들 만들기     → 분석 수치 + 원본 코드 일부를 markdown으로 합침 (~90KB 한도)
       ↓
[3] AI 호출        → 번들을 codex/claude CLI 에 통째로 던지고 해석 받음 (~30-90초)
       ↓
[4] 합성          → 결정론 결과 + AI 해석 + vibe_insights 를 한 payload 로
       ↓
[5] SPA 렌더      → React 가 payload 받아 화면 그림
```

핵심 원칙(`docs/intent.md` Learnings): **결정론이 증거 수집, AI 가 해석.** 순수 규칙은 맥락 없고 순수 AI 는 근거 없음 — 둘을 결합.

## 1) 결정론 분석 (`src/codexray/*`)

레포 경로 받으면 Python만으로 다음을 *각각 독립* 실행:

| 모듈 | 역할 |
|---|---|
| `inventory.py` | 파일 수, 언어 분포, 디렉토리 구조 |
| `graph/` | 언어별 파서로 import 의존성 그래프 |
| `metrics/` | 라인 수·복잡도·fan-in/fan-out |
| `quality/` | A~F 등급 + 차원별 점수 |
| `hotspots/` | 자주 바뀌고 결합도 높은 파일 (git log + graph) |
| `entrypoints/` | CLI · API · main 함수 진입점 |
| `vibe/` | 바이브코딩 흔적 (CLAUDE.md 존재, Co-Authored-By 패턴 등) |
| `briefing/git_history.py` | 커밋 타임라인, 프로세스 vs 코드 비율 |
| `vibe_insights/axes.py` | 3축 점수 산정 |

이 시점까지 AI 없음. 결과는 모두 dataclass 로 직렬화.

## 2) 번들 만들기 (`web/ai_briefing.py:build_raw_code_bundle`)

위 결정론 결과를 *그대로* AI 에게 주지 않음. 대신:

- **핵심 문서 통째 첨부**: README, CLAUDE.md, AGENTS.md, docs/intent.md, openspec/project.md, docs/constraints.md (있으면)
- **원본 코드 일부**: 진입점 파일들 + coupling 상위 파일들 (파일 통째 또는 head/tail 잘라서)
- **보조 메트릭 텍스트**: inventory·metrics·quality·hotspots 의 *핵심 수치* 를 짧은 markdown 으로

전체 번들 크기 한도 **90KB**. codex/claude CLI 의 토큰 한도 ~200K, 한국어 prose 3 chars/token 가정한 안전 마진.

→ 결과: 한 덩어리 markdown 텍스트.

## 3) AI 호출 (`web/ai_briefing.py:_call_ai_for_briefing`)

```
prompt = build_ai_briefing_prompt(bundle_markdown)
        ↓
        시스템 instruction (페르소나·톤·JSON 형식 강제·ai_prompt 6 라벨 규칙) +
        ↓
        bundle markdown (위 단계 산출물)
        ↓
codex CLI 시도 → 실패 시 claude CLI 폴백 → 둘 다 실패 시 결정론 폴백
        ↓
응답 = JSON 블록 ({ executive, architecture, quality_risk, next_actions[],
                  key_insight, intent_alignment })
```

**핵심**: AI 는 *수치만* 받는 게 아니라 *코드 자체* 도 읽음.

캐싱: 응답을 `~/.cache/codexray/ai-briefing/<sha256>.json` 에 저장. 캐시 키에 `PROMPT_VERSION` 포함되니 prompt 바뀌면 자동 무효화.

## 4) 합성 (`web/briefing_payload.py:build_briefing_payload`)

결정론 결과 + AI 해석 + vibe_insights 를 *한 JSON payload* 로 묶음.

이 단계의 핵심 작업:
- `next_actions` 를 카테고리별로 분류 (code / structural / vibe_coding)
- `vibe_coding` 카테고리는 AI 가 만들지 *않음* — `vibe_insights` 의 axis-weakness 데이터에서 *합성*
- 폴백 로직: AI 실패 시 결정론 데이터만으로 카드 만듦

이 시점에서 `schema_version` 박힘.

## 5) SPA 렌더 (`frontend/src/`)

React 가 payload 받아서 컴포넌트 트리로 그림. 주요:
- `BriefingScreen.tsx` — 5섹션 위계
- `NextActionsSection.tsx` — 카테고리별 카드 + ai_prompt 복사 버튼
- 미시 탭 9개 — 결정론 raw 데이터를 직접 그래프·표로

## AI 가 받는 것 vs AI 가 못 보는 것

**AI 가 받음**:
- 결정론 분석의 핵심 수치 (등급, hotspot 개수, fan-in 분포 요약 등)
- 진입점 파일 + coupling 상위 파일의 *원본 소스* (head/tail 잘라서)
- 핵심 문서 (README, CLAUDE.md 등) 통째

**AI 가 못 봄** (90KB 제한):
- coupling 하위 파일들 (long tail)
- 결정론 분석에서 hotspot 으로 안 잡힌 파일
- 외부 도구 (Notion / Slack / Linear 등 — 파일 시스템 밖)

## 시간 분포

- 결정론 분석: ~5초
- 번들 직렬화: <1초
- AI 호출: 30-90초 (codex/claude CLI)
- 합성·직렬화: <1초
- SPA 렌더: <1초 (이미 dist 빌드돼 있음)

총 ~30-90초. 결정론 부분만 별도 endpoint(`/api/inventory`, `/api/graph` 등) 로 호출하면 5초 내 결과.

## 미래 개선 후보 — Python·AI 상호보완 최적화

**문제 제기 (2026-05-01)**: 현재 흐름이 *결정론이 사실 수집, AI 가 해석* 으로 잘 분리돼 있지만, 결정론이 AI 의 효율을 떨어뜨리는 측면도 있음.

구체 위험:
1. **앵커링** — bundle 에 등급/수치가 박히면 AI 가 재평가 없이 받아씀. 결정론이 틀리면 AI 도 같이 틀림.
2. **Long tail 미노출** — 90KB 한도 밖 파일은 AI 가 못 봄. 흥미로운 게 long tail 에 있을 때 발견 실패.
3. **토큰 예산 분할** — 메트릭 텍스트가 자리 잡으면 *원본 코드* 비중 줄어듬. 코드를 더 줘야 AI 가 더 잘 봄.
4. **JSON 스키마 경직** — AI 가 정해진 필드 외에 *발견한 통찰* 을 표현할 자리 없음.
5. **과번역 요청** — "메트릭 용어 쓰지 마" 가 *정확성* 을 깎음 (예: "fan-in 5" → "한 파일에 의존 *조금* 몰림" — 5 가 어느 정도인지 사라짐).

개선 방향 (별도 변경 후보, 가칭 `bundle-composition-rebalance`):
- 번들에서 메트릭 텍스트 비중 ↓, 원본 코드 비중 ↑
- bundle 에 "우리가 *못 본 것*" 메타 정보 추가 ("이 외에 N 개 파일, K 라인 — 의심 가는 게 있으면 말해")
- JSON 스키마에 `additional_observations` 자유 필드 추가
- 앵커링 차단 실험: bundle 에서 결정론 수치 빼고 AI 한테 직접 판단시킨 다음 결정론 결과와 비교 → 일치도 측정

**목표**: Python 분석과 AI 분석이 *서로의 약점을 채우는* 관계로 가져가서 최상의 결과 도출. 한쪽이 다른 쪽 정답을 미리 박아두는 관계 ❌, 한쪽이 사실 수집 / 다른 쪽이 *독립적으로* 해석한 후 *상호 검증* ✅.

이번 변경(`vibe-insights-realign`) scope 밖. 후속 변경 후보로 보존.

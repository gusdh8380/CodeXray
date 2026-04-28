## Context

CodeXray의 의도는 명확하다 — 처음 본 레포에 대한 막연함을 없애주고, 코드를 모르는 사람도 "이게 뭐고 / 어떤 상태고 / 뭘 먼저 봐야 하는지" 한 화면에서 파악하게 한다. 그런데 현재 구현은 의도에서 멀어졌다.

**현재 상태의 문제:**
- Briefing이 PPT 슬라이드 6장을 데이터로만 보유하고 화면에 제대로 노출하지 않음
- AI 해석은 처리된 JSON 메트릭만 입력받아 "이게 뭐 하는 프로젝트인지"의 맥락이 약함
- 바이브코딩 인사이트가 단순 체크리스트 수준이고 "잘했냐"의 판단 기준이 모호
- 프론트엔드가 htmx + Jinja 부분 렌더링이라 발표 자료 수준의 시각 품질에 도달하기 어려움
- 분석하기 버튼처럼 "이미 있어야 할 것"을 명시적으로 강조하다 보니 흐름이 끊김

이번 변경은 의도와의 정렬을 회복하기 위한 것이며, 따라서 부분 수정이 아니라 Briefing 화면의 콘텐츠·정보 구조·렌더링 스택을 모두 바꾼다.

## Goals / Non-Goals

**Goals:**
- Briefing 화면 하나에서 매크로 방향 잡기 완성: 5개 섹션이 위에서 아래로 자연스럽게 읽힘
- 바이브코딩 인사이트가 핵심 차별점이 됨 — 자동 판별 + 3축 평가 + 타임라인 + 행동/왜
- AI가 원본 소스코드와 git history를 직접 읽고 서술 생성
- 발표 품질의 UI — React + Tailwind + shadcn/ui로 시각적 일관성 확보
- 미시 분석(Quality, Hotspots, Graph 등)으로의 자연스러운 진입
- 단일 명령(`codexray serve`)으로 동일하게 실행됨 — 빌드 결과물을 FastAPI가 정적 서빙

**Non-Goals:**
- 시니어 개발자 깊이 만족 (후속 변경으로 분리)
- Dashboard 시각화 개선 (이름만 변경, 내부 그래프 알고리즘 개선은 후속)
- 모바일 반응형 (로컬 데스크톱 우선)
- 다국어 지원 (한국어만)
- SaaS화, 외부 호스팅
- 코드 자동 수정 기능

## Decisions

### 1. 프론트엔드 스택: React + Vite + Tailwind + shadcn/ui

**왜:**
- 발표 품질의 UI가 의도의 핵심이고 htmx로는 시각 일관성에 한계가 있음
- shadcn/ui가 즉시 사용 가능한 깔끔한 컴포넌트 제공 (Card, Tabs, Skeleton, Progress 등)
- AI 어시스턴트 학습 데이터가 가장 풍부 → 유지보수 비용 낮음
- Vite 빌드 결과물(`frontend/dist/`)을 FastAPI가 정적 서빙하면 단일 프로세스 유지

**대안 검토:**
- **htmx 유지 + Tailwind 추가** — 빌드 단계는 안 늘지만 컴포넌트 라이브러리 부족, 슬라이드/타임라인 같은 풍부한 인터랙션 만들기 어려움
- **SvelteKit** — 코드는 더 깔끔하지만 컴포넌트 생태계 작음
- **Tauri 데스크톱** — 의도 문서의 "로컬 실행 우선"과 정렬되지만 빌드/배포 복잡도 큼

**Trade-off:** Node.js 빌드 의존성 추가. 개발자가 `npm install`/`npm run build` 단계를 거쳐야 함. CI에서 두 언어 빌드가 필요. 이 비용은 UI 품질을 위한 투자로 수용.

### 2. 백엔드는 JSON API로 단일화

**왜:**
- 프론트엔드를 SPA로 가는 순간 HTML fragment 응답은 의미가 없음
- 모든 endpoint가 일관된 JSON 모델을 반환하면 프론트의 컴포넌트화가 자연스러움
- 기존 분석 빌더(inventory, graph, metrics 등)는 이미 dataclass 기반이라 JSON 변환은 직접적

**구체적 매핑:**
- `GET /` → `frontend/dist/index.html` 정적 응답
- `POST /api/briefing` → background job 시작, JSON `{ jobId, status, step }`
- `GET /api/briefing/status/{job_id}` → 진행/완료 JSON
- `POST /api/{tab}` → 분석 결과 JSON (HTML fragment 폐기)
- `POST /api/browse-folder` → 선택된 path JSON

**Trade-off:** 기존 render.py의 한국어 텍스트 변환 로직 일부가 프론트엔드로 이동. 백엔드는 raw 데이터만 반환하고 표시 로직은 프론트엔드가 책임.

### 3. AI 입력: 처리된 JSON → 원본 소스코드 + git history

**왜:**
- "이 프로젝트가 뭐 하는 건지"는 처리된 메트릭에서 안 나옴 (53 files, D grade는 정체를 안 알려줌)
- 원본 코드를 보면 LLM이 도메인, 의도, 명명 규칙을 직접 읽고 맥락을 잡음
- git history는 개발 흐름의 1차 증거

**구체적 입력 번들 구조:**
```
{
  "repo_name": "...",
  "tree_summary": "...",  // 디렉토리 트리 요약
  "key_files": [
    { "path": "...", "content": "..." }  // README, CLAUDE.md, main entry, 상위 hotspot
  ],
  "git_history": {
    "commit_count": ..,
    "recent_commits": [...],
    "process_commits": [...]
  },
  "metrics_summary": { ... }  // 보조 자료, 핵심 수치만
}
```

**파일 선택 전략:**
- README.md, AGENTS.md, CLAUDE.md, docs/intent.md (있다면 무조건)
- 진입점 파일 1-2개 (entrypoints 분석 결과 활용)
- coupling 상위 3개 파일 (hotspots 분석 결과 활용)
- 토큰 제한 (예: 60K tokens) 안에서 잘라냄

**대안 검토:**
- **모든 파일 보내기** — 토큰 폭발, 비용 폭증, 의미 있는 파일이 묻힘
- **현재처럼 메트릭만 보내기** — 맥락 부족 (현재 문제)

### 4. 바이브코딩 인사이트: 3축 평가 + 자동 판별

**왜:**
- 단일 점수보다 3축이 "어디가 약한지"를 명확하게 보여줌
- 자동 판별이 있으면 미감지 레포에는 시작 가이드를 보여줄 수 있어 사용자 폭이 넓어짐

**3축 정의:**

| 축 | 측정 대상 | 입력 |
|---|---|---|
| ① 환경 구축 | AI가 일할 수 있는 기반 (CLAUDE.md, AGENTS.md, openspec/, .claude/) | 파일 존재 + 내용 신호 |
| ② 개발 과정 깔끔함 | AI가 의도대로 달렸는지 (fix/feat 비율, 명세 → 코드 순서, intent drift) | git log + AI 해석 |
| ③ 이어받기 가능성 | 다음 세션이 문맥 없이 시작 가능한지 (검증·테스트·회고·인수인계) | 파일 존재 |

**자동 판별 신호 가중치:**
- 강한 신호 (즉시 감지): CLAUDE.md, AGENTS.md, .claude/, .omc/, openspec/, `Co-Authored-By: Claude` 커밋
- 중간 신호 (가중치): docs/validation/, docs/vibe-coding/, conventional commit + 한국어 혼재 패턴
- 약한 신호 (힌트): README의 Claude/GPT/Cursor 언급

**점수 계산:** 0-100 스케일, 각 축 독립 계산. 종합 점수는 평균이 아니라 약점 강조 ("환경은 좋지만 과정이 약함" 식 서술).

### 5. Briefing 화면 5개 섹션 구조

```
┌──────────────────────────────────────┐
│ 1. 이게 뭐야 (Hero)                   │
│    - AI 한 문단 요약                  │
│    - 핵심 수치 3개 (files, language, grade) │
├──────────────────────────────────────┤
│ 2. 어떻게 만들어졌나                   │
│    - 구조·아키텍처 서술               │
│    - 주요 파일 강조                  │
├──────────────────────────────────────┤
│ 3. 지금 상태                         │
│    - 품질 신호를 평어로              │
│    - 위험 위치                       │
├──────────────────────────────────────┤
│ 4. 바이브코딩 인사이트 ★              │
│    - 3축 점수 (감지된 경우)           │
│    - 개발 과정 타임라인              │
│    - AI 종합 해석                    │
│    - 미감지 시: 시작 가이드           │
├──────────────────────────────────────┤
│ 5. 지금 뭘 해야 해                    │
│    - 행동 + 왜 + 분석 증거 인용 (3개) │
└──────────────────────────────────────┘
```

각 섹션 우측에 "관련 미시 탭으로" 링크 (예: 3번 → Quality 탭).

### 6. 미시 분석 탭 처리

기존 11개 탭(Overview, Inventory, Graph, Metrics, Quality, Hotspots, Report, Review, Entrypoints, Dashboard, Vibe Coding)은 React 컴포넌트로 포팅하여 **Briefing 아래 별도 영역**에 둔다. 접힌 상태가 기본 (의도: Briefing이 메인). 사용자가 펼치면 탭 네비게이션 표시.

**Dashboard 처리:** "구조 그래프" 또는 "의존성 지도" 같은 한국어 이름으로 변경. iframe 콘텐츠는 그대로 (개선은 후속 변경).

### 7. 진행 상태 UX

AI 해석이 30-90초 걸리는 동안 "지금 뭐 하는 중"을 항상 표시:

```
1. 파일 트리 수집 중...
2. 핵심 파일 읽는 중...
3. git history 분석 중...
4. AI 해석 요청 중... (~30s)
5. 결과 정리 중...
완료
```

각 단계는 구체적이라 "AI 해석 중..."이 30초 동안 멈춰 보이지 않음. 진행률 바와 단계 텍스트를 React 컴포넌트로 표현.

## Risks / Trade-offs

- **[Risk] Node.js 빌드 의존성 추가** → 개발자/CI 부담 증가
  - **Mitigation:** README에 한 번 빌드하면 끝나는 절차 명시, `frontend/dist/`를 git에 커밋하지 않더라도 release tag에서는 미리 빌드
- **[Risk] 원본 코드를 CLI에 보내는 것이 토큰 비용 폭증** → codex 사용량 증가
  - **Mitigation:** 파일 선택 전략으로 60K 토큰 이내 제한, 캐시 기반 재사용 강화
- **[Risk] 바이브코딩 자동 판별이 잘못 감지** → 전통 레포에 잘못된 인사이트 표시
  - **Mitigation:** 약한 신호만으로는 감지 처리하지 않음, 강한 신호 1개 이상 또는 중간 신호 2개 이상으로 임계 설정
- **[Risk] React 도입으로 페이지 첫 로드 시간 증가** → "발표 자료" 의도와 충돌
  - **Mitigation:** Vite 코드 분할, 초기 번들 < 200KB 목표, lazy 로딩
- **[Risk] 미시 분석 탭들의 React 포팅 작업량 큼** → 일정 risk
  - **Mitigation:** 첫 단계에서는 Briefing + 시각 품질에 집중, 미시 탭은 점진적 포팅. JSON API가 준비되면 미시 탭은 단순 변환 작업
- **[Risk] 기존 사용자(테스트, 캐시)와의 호환성 깨짐**
  - **Mitigation:** 본 변경이 BREAKING. 캐시는 prompt version 변경으로 자동 무효화. 기존 archive된 변경들은 영향 없음

## Migration Plan

1. `frontend/` 디렉토리에 React + Vite + Tailwind + shadcn/ui 스캐폴드 생성
2. FastAPI route를 JSON 응답 + 정적 서빙으로 변경 (기존 htmx 라우트는 일시적 유지)
3. Briefing 5개 섹션 + 바이브코딩 인사이트 + 타임라인 React 컴포넌트 구현
4. AI 입력 포맷을 raw code bundle로 교체
5. 미시 분석 탭들을 점진적으로 React로 포팅
6. 기존 htmx 코드(`templates/`, `static/`, `render.py`의 HTML 부분) 제거
7. 기존 active 변경들(briefing-as-product, humanize-analysis-output)을 archive
8. CivilSim/CodeXray 자체 분석으로 검증

**Rollback:** 본 변경은 BREAKING이므로 롤백은 git revert. 중간 커밋들은 호환성을 깨지 않도록 점진적으로 만들지만, 최종 상태는 React-only.

## Open Questions

- 미시 분석 탭들의 React 포팅 우선순위는? (Briefing 의존도 높은 것부터?)
- 다음 행동의 "왜" 텍스트를 AI가 매번 새로 생성할지, 아니면 결정론적 템플릿 + AI 보강일지
- 타임라인 시각화의 정확한 형태 (수직 타임라인 vs swim lane) — 디자인 단계에서 프로토타입으로 결정
- 바이브코딩 미감지 시 "시작 가이드"의 콘텐츠 깊이는 어디까지인가 (Quick start vs 전체 프로세스 설명)

## Context

`non-roboco-validation` 결과 문서 §3.1·§5.3 에서 fastapi NOT DETECTED 가 도구의 가장 큰 사용성 결함으로 식별됐다. 사용자(프로젝트 오너) 와 옵션 A/B/C 를 검토 후 옵션 A' 을 채택:

- 옵션 A 와의 차이: A' 는 비감지 시 *시작 가이드도 제거*. 시작 가이드가 비-AI 프로젝트 사용자에게 부적절한 권유 (CLAUDE.md 작성하라 등) 였다.
- 페르소나 매핑:
  - 동료 (1순위, 비개발자 vibe coding 학습자): 자기 vibe coding 프로젝트만 분석. detection 항상 양성. 화면 변화 없음.
  - 본인 (2순위, 일반 OSS 분석가): fastapi 같은 비-AI OSS 분석 시 vibe insights 섹션 자동 사라짐 → *깔끔한 일반 분석 도구* 로 변신.

이해관계자 결정 트레일: `docs/validation/non-roboco-validation-results.md` §5.3 → 사용자 직접 옵션 A' 선택.

## Goals / Non-Goals

**Goals:**
- detection 게이트 (`CLAUDE.md/AGENTS.md/.claude/.omc/openspec/Co-Authored-By:Claude`) 는 *그대로* 유지.
- 비감지 시 vibe insights 섹션 응답 자체를 *제거* 하고 프론트엔드도 렌더링 건너뜀.
- starter_guide 모듈·컴포넌트·타입 *완전 제거*. fallback 자료 안 남김.
- 두 페르소나 모두에서 자연스러운 화면이 나오도록 검증.

**Non-Goals:**
- detection 알고리즘 변경. 신호 풀 변경. 임계값 변경. — 모두 후속 변경 (`vibe-signal-pool-expand` / `vibe-thresholds-tune`).
- "vibe coding 처음 시작하기" 가이드를 어디로 이동시킬지 결정. — README 또는 별도 문서 검토는 본 변경 밖.
- 비감지 프로젝트의 *대안 평가* (옵션 B/C 의 책임감 진단) 도입.

## Decisions

### 결정 1: `build_vibe_insights` 의 비감지 분기 — `None` 반환

현재: `{"detected": False, "starter_guide": [...], "blind_spots": [...]}` 반환.

변경: 비감지 시 함수가 `None` 반환. 호출자(`build_briefing_payload`)가 None 을 받아 페이로드의 `vibe_insights` 필드를 *키 자체 부재* 또는 `null` 로 설정.

**대안 — 빈 dict 반환**: 호출자가 매번 `if vibe_insights and vibe_insights["detected"]` 체크해야 함. 더 장황. 기각.

**대안 — `{"detected": False}` 만 반환**: 프론트엔드가 이걸 받아 "비감지 메시지" 를 보여줄 수 있음. 그러나 "비감지 메시지" 자체가 비-AI 프로젝트 사용자에게 *vibe coding 을 강요하는 인상* 이라 옵션 A' 의 의도와 정면 충돌. 기각.

→ **None 채택.** 응답 schema 가 명백히 *섹션 부재* 를 나타냄.

### 결정 2: starter_guide 모듈 완전 삭제

`src/codexray/vibe_insights/starter_guide.py` 와 그 테스트 / 프론트엔드 컴포넌트(`StarterGuide`, `StarterGuideCard`) / 타입(`StarterGuideItem`) 모두 삭제.

**대안 — 코드 보존, 호출만 비활성화**: "나중에 살릴지도" 라는 가능성 때문에 코드 잔재 유지. 그러나 *"나중에 살릴지도"* 는 옵션 B/C 로 가는 길이고 그건 본 변경의 *non-goal*. 코드 잔재는 회귀 위험만 키움. 기각.

→ **완전 삭제.** 향후 옵션 B/C 로 되돌아갈 일 있으면 git history 에서 복구.

### 결정 3: SCHEMA_VERSION 6 → 7

응답 형태가 변경 (vibe_insights 필드의 None 가능성, starter_guide 부재) 되므로 SCHEMA_VERSION bump. 캐시 자동 무효화.

**대안 — bump 안 함**: 캐시 hit 시 이전 형태가 그대로 반환되어 프론트엔드가 깨짐. 기각.

### 결정 4: codebase-briefing 의 `vibe_coding` 카테고리 합성 규칙 단순화

현재 시나리오: "vibe_coding 카테고리 항목은 `vibe_insights.next_actions` 또는 `vibe_insights.starter_guide` 에서 합성".

변경: starter_guide 가 사라지므로 시나리오에서 `또는 vibe_insights.starter_guide` 부분 제거. `vibe_insights` 가 None 일 때는 vibe_coding 카테고리 카드가 *빈 리스트* (이미 dynamic policy 로 0–3 허용).

### 결정 5: 프론트엔드 — 조건부 렌더링이 기본 패턴

`BriefingScreen.tsx` 의 `<VibeInsightsSection />` 위에 조건문:

```tsx
{data.vibe_insights && <VibeInsightsSection data={data.vibe_insights} />}
```

`VibeInsightsSection.tsx` 자체에서 `data.detected === False` 분기 (StarterGuide) 도 *제거* — 이 컴포넌트는 항상 detected=True 데이터만 받음을 가정.

**대안 — VibeInsectionSection 내부에서 비감지 처리**: 호출자는 항상 컴포넌트 호출. 그러나 비감지 시 *아무것도 안 그림* 인 컴포넌트는 의도 모호. 호출자에서 조건 분기가 명확. 채택.

### 결정 6: AI 호출 — vibe coding 흔적 비감지 시 vibe 관련 prompt 전체 스킵

`ai_briefing.py` 의 `build_ai_briefing_prompt` 가 vibe insights 데이터를 prompt 컨텍스트로 사용. 비감지 시 그 부분을 prompt 에서 제거 → AI 출력에서 vibe 관련 narrative 도 자동 누락. AI 호출 비용 절감 + 비-AI 프로젝트에 대한 vibe 권유 차단.

## Risks / Trade-offs

- [vibe coding 학습자가 비감지 프로젝트 분석 시 *어떻게 시작해야 하는지 단서* 가 도구 안에서 사라짐] → README / 메인 페이지 도움말에 외부 자료 (Anthropic Best Practices, OpenAI Codex AGENTS.md guide) 링크. *별도 변경* 으로 분리.
- [BREAKING: 응답 schema 변경] → SCHEMA_VERSION 6 → 7 bump 로 캐시 자동 무효화. SPA 단일 클라이언트라 외부 호환성 영향 거의 없음.
- [starter_guide 삭제 후 옵션 B/C 로 되돌아갈 때 코드 재구축 비용] → 옵션 B/C 는 detection 자체를 바꾸는 큰 변경이라 어차피 starter_guide 와 다른 구조. 재사용 가능성 낮음. 위험 무시.
- [비감지인데 사용자가 "내 프로젝트 vibe coding 인 것 같은데 왜 안 잡혔지?" 의문] → detection 신호가 명시적이라 사용자가 자기 프로젝트에 CLAUDE.md/AGENTS.md 추가하면 즉시 감지 전환. 이미 자명.

## Migration Plan

1. **백엔드 변경 단계**:
   - `vibe_insights/builder.py` 비감지 분기 None 반환
   - `vibe_insights/starter_guide.py` 삭제 + `__init__.py` export 정리
   - `web/briefing_payload.py` None 처리 + SCHEMA_VERSION 7
   - `web/ai_briefing.py` 비감지 시 vibe prompt 부분 스킵
   - 백엔드 테스트 갱신: starter_guide 관련 제거, 비감지 None 반환 테스트 추가
2. **프론트엔드 변경 단계**:
   - `lib/api.ts` `VibeInsights` 타입 옵셔널화, `StarterGuideItem` 제거
   - `BriefingScreen.tsx` 조건부 렌더링
   - `VibeInsightsSection.tsx` StarterGuide 분기 제거
3. **검증**:
   - 자기 적용 (`docs/validation/vibe-detection-rebalance-self.md`) — 동료 페르소나 시뮬레이션, vibe insights 섹션 정상
   - fastapi 적용 (`docs/validation/vibe-detection-rebalance-fastapi.md`) — 본인 페르소나 시뮬레이션, vibe insights 섹션 사라짐
4. **롤백**: git revert. SCHEMA_VERSION 다시 6 으로 내리는 게 아니라 revert 하면 캐시는 어차피 새 키로 분리됨.

## Open Questions

- 비감지 프로젝트 분석 시 화면 위에 *"이 프로젝트에는 AI 협업 흔적이 없어 vibe coding 진단을 건너뜁니다"* 같은 한 줄 안내를 보여줄지 여부. 후보:
  - (A) 안 보여줌 — 깔끔. 사용자가 의문을 안 가질 수도. 채택 가능.
  - (B) 한 줄 보여줌 — 사용자가 "왜 vibe insights 가 없지?" 궁금할 때 답.
  - **결정 보류**. 자기 적용·fastapi 적용 검증 시 사용자가 직접 보고 결정. design 단계에서 강제하지 않음.
- 본 변경 후 README 에 vibe coding 외부 자료 링크 추가는 별도 변경으로 분리. 본 변경에서 README 건드리지 않음.

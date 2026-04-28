## 1. 프론트엔드 스캐폴드

- [x] 1.1 `frontend/` 디렉토리에 `npm create vite@latest -- --template react-ts` 로 React + TypeScript + Vite 프로젝트 생성
- [x] 1.2 Tailwind CSS v4 설치 및 `@tailwindcss/vite` 플러그인 + `src/index.css` shadcn 테마 토큰 설정
- [x] 1.3 shadcn 친화 컴포넌트 직접 작성 (Card, Button, Input, Badge, Progress) + cn() 헬퍼
- [x] 1.4 `frontend/.gitignore`에 `node_modules`, `dist` 포함됨 (Vite 기본값)
- [x] 1.5 `frontend/vite.config.ts`에 `outDir: 'dist'` 설정
- [ ] 1.6 README에 프론트엔드 빌드 절차(`cd frontend && npm install && npm run build`) 추가

## 2. FastAPI를 JSON API로 전환

- [ ] 2.1 `src/codexray/web/routes.py`의 모든 분석 endpoint 응답을 JSON으로 변경 (briefing, overview, inventory, graph, metrics, entrypoints, quality, hotspots, report, vibe-coding-insights, review)
- [ ] 2.2 `src/codexray/web/render.py`의 HTML 생성 로직 제거, dataclass → JSON 직렬화 헬퍼만 유지
- [ ] 2.3 `src/codexray/web/jobs.py`의 background job 응답을 JSON status 응답으로 변경
- [ ] 2.4 `src/codexray/web/app.py` 에서 `frontend/dist/`를 정적 자산으로 마운트하고 `GET /` 가 `index.html` 반환
- [ ] 2.5 `src/codexray/web/templates/`, `src/codexray/web/static/` 디렉토리 삭제
- [ ] 2.6 `tests/test_web_ui.py` 의 HTML fragment 어서션을 JSON 응답 어서션으로 교체

## 3. AI 입력을 원본 코드 번들로 교체

- [ ] 3.1 `src/codexray/web/ai_briefing.py`의 `build_evidence_bundle()` 를 raw code bundle 빌더로 교체 (README, AGENTS.md, CLAUDE.md, docs/intent.md, 진입점 파일, 상위 hotspot 파일)
- [ ] 3.2 토큰 제한(예: 60K) 안에서 파일을 자르는 헬퍼 추가
- [ ] 3.3 보조 메트릭(inventory/metrics/quality/hotspots 핵심 수치)을 bundle에 함께 포함
- [ ] 3.4 AI 프롬프트를 5개 섹션 별 한국어 서술 + 행동+왜+증거 형식 next_actions를 JSON으로 반환하도록 재작성
- [ ] 3.5 `parse_ai_briefing_response()` 를 새 응답 구조에 맞게 갱신
- [ ] 3.6 캐시 키에 prompt version 포함, 기존 캐시 자동 무효화
- [ ] 3.7 codex 우선, claude 폴백 동작 검증 테스트 추가

## 4. 바이브코딩 인사이트 모듈 (백엔드)

- [ ] 4.1 `src/codexray/vibe_insights/__init__.py` 패키지 생성
- [ ] 4.2 `src/codexray/vibe_insights/detection.py` 작성 — 강한·중간·약한 신호 가중치로 감지/미감지 판별
- [ ] 4.3 `src/codexray/vibe_insights/axes.py` 작성 — 환경 구축 / 개발 과정 / 이어받기 점수 계산기
- [ ] 4.4 `src/codexray/vibe_insights/timeline.py` 작성 — git history에서 프로세스 단계 도입 시점과 코드/프로세스 비율 추출
- [ ] 4.5 `src/codexray/vibe_insights/next_actions.py` 작성 — 행동+왜+증거 트리플 생성 (분석 결과 인용)
- [ ] 4.6 `src/codexray/vibe_insights/starter_guide.py` 작성 — 미감지 레포에 대한 시작 가이드 생성
- [ ] 4.7 `src/codexray/vibe_insights/builder.py` 작성 — 모든 모듈 조합해 `VibeCodingInsights` dataclass 반환
- [ ] 4.8 결정론적 직렬화(JSON, schema_version 1) 보장 테스트
- [ ] 4.9 CivilSim 분석 시 감지+3축 점수가 의미 있는 값을 내는지 검증 테스트

## 5. Briefing 빌더 재구성

- [ ] 5.1 `src/codexray/briefing/build.py` 를 5개 섹션 모델(`what` / `how_built` / `current_state` / `vibe_insights` / `next_actions`)로 재작성
- [ ] 5.2 schema_version을 2로 올리고 기존 PPT 슬라이드 / Card / Slide 데이터 구조 제거
- [ ] 5.3 vibe_insights 섹션은 4번에서 만든 모듈 결과를 그대로 포함
- [ ] 5.4 결정론적 부분의 직렬화 안정성 테스트 갱신
- [ ] 5.5 AI 서술 파트는 별도 캐시에서 가져와 합치는 헬퍼 추가
- [ ] 5.6 `tests/test_briefing.py` 의 어서션을 새 5섹션 구조로 교체

## 6. 진행 상태 UX

- [ ] 6.1 `src/codexray/web/jobs.py` 의 단계 텍스트를 "파일 트리 수집 중…", "핵심 파일 읽는 중…", "git history 분석 중…", "AI 해석 요청 중…", "결과 정리 중…" 으로 갱신
- [ ] 6.2 status 응답에 `step`, `progress`, `eta_hint` 필드 포함
- [ ] 6.3 단계 진행 시 부드러운 갱신을 위해 progress 가 0~1 사이 단조 증가하도록 설계

## 7. SPA 핵심 화면 구현

- [ ] 7.1 `frontend/src/App.tsx` 와 라우팅(필요 시 react-router) 작성, 메인은 path input + 결과 영역
- [ ] 7.2 `frontend/src/components/PathInput.tsx` — Enter 키와 최근 path selector 통합, 분석하기 버튼 없음
- [ ] 7.3 `frontend/src/components/RecentPaths.tsx` — localStorage 기반 최근 path 저장/표시 (최대 5개)
- [ ] 7.4 `frontend/src/components/ThemeToggle.tsx` — 라이트/다크 테마 토글, localStorage 영속
- [ ] 7.5 `frontend/src/lib/api.ts` — JSON API 호출 헬퍼 (briefing 시작/polling, 미시 endpoint)
- [ ] 7.6 `frontend/src/components/BriefingProgress.tsx` — 단계 텍스트 + Progress 컴포넌트로 진행 상태 표시

## 8. Briefing 5개 섹션 컴포넌트

- [ ] 8.1 `frontend/src/components/briefing/WhatSection.tsx` — Hero 영역 (한 문단 + 핵심 수치 3개)
- [ ] 8.2 `frontend/src/components/briefing/HowBuiltSection.tsx` — 구조 서술 + 주요 파일 (Graph 탭 링크)
- [ ] 8.3 `frontend/src/components/briefing/CurrentStateSection.tsx` — 품질 평어 + 위험 (Quality / Hotspots 링크)
- [ ] 8.4 `frontend/src/components/briefing/VibeInsightsSection.tsx` — 3축 점수 카드, AI 종합 서술, 타임라인, 또는 시작 가이드
- [ ] 8.5 `frontend/src/components/briefing/NextActionsSection.tsx` — 행동/왜/증거 카드 3개
- [ ] 8.6 `frontend/src/components/briefing/BriefingScreen.tsx` — 5개 섹션 수직 레이아웃 + 발표용 시각 품질
- [ ] 8.7 큰 제목, 충분한 여백, Tailwind typography 로 발표 친화적 시각 구현
- [ ] 8.8 라이트/다크 테마 모두에서 시각 일관성 검증

## 9. 바이브코딩 타임라인 시각화

- [ ] 9.1 `frontend/src/components/vibe/VibeAxisCard.tsx` — 단일 축 점수 카드 (점수 + 약점 항목 목록)
- [ ] 9.2 `frontend/src/components/vibe/VibeTimeline.tsx` — 개발 과정 타임라인 (수직 형태로 시작, 추후 swim lane 검토)
- [ ] 9.3 `frontend/src/components/vibe/VibeStarterGuide.tsx` — 미감지 시 시작 가이드 카드
- [ ] 9.4 가장 약한 축을 강조 표시 (색상 또는 라벨)
- [ ] 9.5 타임라인 데이터가 비어있을 때 폴백 메시지 표시

## 10. 미시 분석 영역 포팅

- [ ] 10.1 `frontend/src/components/micro/MicroAnalysisArea.tsx` — 접힌 상태 기본의 collapsible 영역
- [ ] 10.2 `frontend/src/components/micro/OverviewTab.tsx` — Strengths/Weaknesses/Next Actions 카드 + summary 메트릭
- [ ] 10.3 `frontend/src/components/micro/InventoryTab.tsx` — 언어/파일 목록 (LoC 규모 레이블 포함)
- [ ] 10.4 `frontend/src/components/micro/GraphTab.tsx` — 의존성 그래프 데이터 표시
- [ ] 10.5 `frontend/src/components/micro/MetricsTab.tsx` — 메트릭 표 (coupling 위험도 레이블, fan-in/out 보조 설명)
- [ ] 10.6 `frontend/src/components/micro/QualityTab.tsx` — 등급 + 한 줄 해석 + 차원별 점수
- [ ] 10.7 `frontend/src/components/micro/HotspotsTab.tsx` — 한국어 카테고리 라벨 적용
- [ ] 10.8 `frontend/src/components/micro/EntrypointsTab.tsx` — 진입점 목록
- [ ] 10.9 `frontend/src/components/micro/ReportTab.tsx` — Markdown report + Strengths/Weaknesses/Actions 섹션
- [ ] 10.10 `frontend/src/components/micro/VibeCodingTab.tsx` — 바이브코딩 증거 상세 (Briefing 인사이트와는 다른 raw 증거)
- [ ] 10.11 `frontend/src/components/micro/StructureGraphTab.tsx` — 기존 dashboard iframe 임베드, 탭 이름은 "구조 그래프" 로 표시
- [ ] 10.12 `frontend/src/components/micro/ReviewTab.tsx` — AI Review 명시 실행, polling, cancel 흐름

## 11. 분석하기 버튼/기존 진입 흐름 정리

- [ ] 11.1 SPA에 분석하기 버튼이 없는지 확인 (Enter / 최근 path 선택만으로 자동 시작)
- [ ] 11.2 path input 변경 후 일정 idle 시 자동 분석을 트리거하지 않도록 — 명시 Enter 또는 selector 클릭만 트리거
- [ ] 11.3 jobs / routes 에서 분석하기 버튼에 의존하던 코드 흔적 제거

## 12. 의존 변경 정리 및 호환성 정리

- [ ] 12.1 `briefing-as-product` 변경의 코드 흔적(분석하기 버튼, detail-tabs, vibe-coding 슬라이드)을 본 변경 코드와 충돌하지 않게 정리하고 기존 변경을 archive 후보로 표시
- [ ] 12.2 `humanize-analysis-output` 변경에서 도입된 한국어 레이블/등급 해석을 백엔드 JSON 필드로 이전 (size_label, risk_label, category_label, grade_interpretation 등)
- [ ] 12.3 `ai-first-analysis` 변경의 step-by-step 진행 UX를 본 변경의 React 컴포넌트로 이전 (개념 보존)

## 13. 검증 및 자기 적용

- [ ] 13.1 `uv run pytest tests/ -x` 전체 통과 확인 — 새 JSON API와 5섹션 구조 어서션 포함
- [ ] 13.2 `cd frontend && npm run build` 성공 확인, 번들 크기 < 250KB 1차 목표
- [ ] 13.3 `codexray serve` 실행 후 `/Users/jeonhyeono/Project/personal/CodeXray` 자체 분석으로 5섹션, 바이브코딩 감지, 3축 점수, 타임라인 모두 의미 있는 값 표시 확인
- [ ] 13.4 `/Users/jeonhyeono/Project/personal/CivilSim` 분석으로 동일 항목 검증
- [ ] 13.5 라이트/다크 테마 토글 검증
- [ ] 13.6 미시 분석 영역 펼치기/접기 + 모든 미시 탭 렌더링 검증
- [ ] 13.7 Review 탭 명시 실행/취소/완료 흐름 검증
- [ ] 13.8 `docs/validation/briefing-rebuild-self.md` 와 `docs/validation/briefing-rebuild-civilsim.md` 작성 — JSON endpoint smoke와 SPA 시각 결과 캡처 요약 포함

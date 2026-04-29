## 1. 프론트엔드 스캐폴드

- [x] 1.1 `frontend/` 디렉토리에 `npm create vite@latest -- --template react-ts` 로 React + TypeScript + Vite 프로젝트 생성
- [x] 1.2 Tailwind CSS v4 설치 및 `@tailwindcss/vite` 플러그인 + `src/index.css` shadcn 테마 토큰 설정
- [x] 1.3 shadcn 친화 컴포넌트 직접 작성 (Card, Button, Input, Badge, Progress) + cn() 헬퍼
- [x] 1.4 `frontend/.gitignore`에 `node_modules`, `dist` 포함됨 (Vite 기본값)
- [x] 1.5 `frontend/vite.config.ts`에 `outDir: 'dist'` 설정
- [ ] 1.6 README에 프론트엔드 빌드 절차(`cd frontend && npm install && npm run build`) 추가

## 2. FastAPI를 JSON API로 전환

- [x] 2.1 `src/codexray/web/api_v2.py`에 9개 JSON endpoint 추가 (briefing, inventory, graph, metrics, entrypoints, quality, hotspots, vibe-coding, dashboard, report, review, browse-folder). 레거시 htmx routes는 overview만 잔존
- [ ] 2.2 `src/codexray/web/render.py` 의 HTML 생성 로직 제거 (overview 외 모두 JSON으로 흡수됨, 후속 세션 정리)
- [x] 2.3 `src/codexray/web/jobs.py` AIBriefingJob/ReviewJob 모두 JSON status로 노출
- [x] 2.4 `src/codexray/web/server.py` 에서 `frontend/dist/`를 정적 자산으로 마운트하고 `GET /` 가 `index.html` 반환
- [ ] 2.5 `src/codexray/web/templates/`, `src/codexray/web/static/` 디렉토리 삭제 (overview 잔존 의존, 후속)
- [x] 2.6 `tests/test_web_ui.py` 의 어서션을 JSON 응답 어서션으로 교체 (322 passing)

## 3. AI 입력을 원본 코드 번들로 교체

- [x] 3.1 `build_raw_code_bundle()` 추가 — CLAUDE.md/AGENTS.md/README/intent.md + 진입점 + 상위 hotspot/coupling 파일을 markdown 번들로 묶음
- [x] 3.2 `_read_truncated()` 헬퍼 — 파일별 18K char 한계, 초과 시 head/tail + 중략 표시
- [x] 3.3 메타데이터·구조·품질 차원 보조 정보를 번들 상단에 포함
- [x] 3.4 AI 프롬프트 재작성 — "직접 코드를 읽고" + 행동/왜/증거 트리플 강제
- [x] 3.5 `parse_ai_briefing_response()` AINextAction 구조 + 레거시 string 호환
- [x] 3.6 PROMPT_VERSION = "v3-action-reason-evidence", schema_version=3 자동 무효화
- [ ] 3.7 codex 우선, claude 폴백 동작 검증 테스트 추가

## 4. 바이브코딩 인사이트 모듈 (백엔드)

- [x] 4.1 `src/codexray/vibe_insights/__init__.py` 패키지 생성, `build_vibe_insights` 공개
- [x] 4.2 `detection.py` — 강한·중간·약한 신호 가중치로 감지/미감지 판별
- [x] 4.3 `axes.py` — 환경 구축 / 개발 과정 / 이어받기 점수 계산기
- [x] 4.4 `timeline.py` — git history에서 프로세스 단계 도입 시점 추출
- [x] 4.5 next_actions 트리플은 ai_briefing.AINextAction이 직접 만들어 briefing_payload가 통과 (별도 모듈 불필요)
- [x] 4.6 `starter_guide.py` — 미감지 레포에 대한 시작 가이드 생성
- [x] 4.7 `builder.py` — 모든 모듈 조합해 dict payload 반환
- [x] 4.8 결정론적 부분 검증 — 5개 단위 테스트 통과
- [x] 4.9 aquaview 분석 시 감지+3축 점수가 의미 있는 값 (53/25/0) 확인됨

## 5. Briefing 빌더 재구성

- [x] 5.1 `src/codexray/web/briefing_payload.py` 가 5개 섹션 모델(`what` / `how_built` / `current_state` / `vibe_insights` / `next_actions`) 반환
- [x] 5.2 schema_version 2, 인라인 details 추가, vibe_insights 모듈로 분리
- [x] 5.3 vibe_insights 섹션은 4번 모듈 결과를 그대로 포함
- [x] 5.4 결정론적 부분의 직렬화 안정성 테스트 (test_vibe_insights.py)
- [x] 5.5 AI 서술 파트는 ai_briefing 캐시에서 가져와 합치는 헬퍼
- [ ] 5.6 `tests/test_briefing.py` 의 어서션을 새 5섹션 구조로 교체 (briefing 모델은 그대로 두고 payload 어댑터에서만 변환됨)

## 6. 진행 상태 UX

- [x] 6.1 단계 텍스트: "Python 분석 중...", "AI 해석 중...", "완료"
- [x] 6.2 status 응답에 `step`, `progress` 필드 포함
- [x] 6.3 progress 0.05 → 0.20 → 0.65 → 1.0 단조 증가

## 7. SPA 핵심 화면 구현

- [x] 7.1 `frontend/src/App.tsx` — path input + 결과 영역 + Welcome
- [x] 7.2 Header가 path input + Browse 버튼 + recent paths 통합
- [x] 7.3 `recent-paths.ts` localStorage 5개 보관
- [x] 7.4 `theme.ts` light/dark 토글 + localStorage 영속
- [x] 7.5 `lib/api.ts` JSON API 호출 헬퍼
- [x] 7.6 `BriefingProgress.tsx` — 단계 텍스트 + Progress 컴포넌트

## 8. Briefing 5개 섹션 컴포넌트

- [x] 8.1-8.5 SectionShell + VibeInsightsSection + NextActionsSection 단일 컴포넌트 패밀리로 통합
- [x] 8.6 `BriefingScreen.tsx` 5개 섹션 수직 레이아웃
- [x] 8.7 큰 제목, 충분한 여백, Tailwind typography 적용
- [ ] 8.8 라이트/다크 테마 모두에서 시각 일관성 브라우저 검증 (후속)

## 9. 바이브코딩 타임라인 시각화

- [x] 9.1 VibeAxisCard 인라인 (3축 점수 + 약점)
- [x] 9.2 Timeline 수직 형태 + 연결선 + 색상 점
- [x] 9.3 StarterGuide 미감지 시 가이드 카드
- [x] 9.4 가장 약한 축 강조 (rose 테두리 + "약점" 배지)
- [x] 9.5 타임라인 데이터가 비어있을 때 recent_commits 폴백

## 10. 미시 분석 영역 포팅

- [x] 10.1 `MicroAnalysisArea.tsx` — collapsible "상세 분석" 영역
- [ ] 10.2 OverviewTab — overview는 briefing의 what 섹션이 대체 (별도 탭 불필요로 판단)
- [x] 10.3 InventoryTab — 언어/파일 목록 + LoC 규모 비중
- [ ] 10.4 GraphTab — 별도 데이터 표 미구현, 구조 그래프(10.11)가 시각화 담당
- [x] 10.5 MetricsTab — 결합도 표 + 위험도 레이블 + fan-in/out 보조 설명
- [x] 10.6 QualityTab — 등급 + 한 줄 해석 + 차원별 카드
- [x] 10.7 HotspotsTab — 한국어 카테고리 라벨
- [x] 10.8 EntrypointsTab — 진입점 목록 + 종류별 그룹
- [x] 10.9 ReportTab — SWA 카드 + recommendations + 원본 markdown 토글
- [x] 10.10 VibeCodingTab — 바이브코딩 raw 증거 상세
- [x] 10.11 StructureGraphTab(GraphTab) — dashboard iframe 임베드
- [x] 10.12 ReviewTab — AI Review 명시 실행 + polling + cancel

## 11. 분석하기 버튼/기존 진입 흐름 정리

- [x] 11.1 SPA에 분석하기 버튼 없음 (Enter / Browse / 최근 path만 트리거)
- [x] 11.2 path input 변경 후 자동 분석 트리거 안 함
- [x] 11.3 jobs / routes 정리 (분석하기 버튼 의존 코드 모두 SPA로 대체됨)

## 12. 의존 변경 정리 및 호환성 정리

- [x] 12.1 `briefing-as-product` 변경 archive 됨 (analyze 버튼/detail-tabs/vibe 슬라이드 모두 SPA로 대체됨)
- [x] 12.2 한국어 레이블 (size_label, risk_label, category_label, grade_interpretation) 모두 React 컴포넌트가 직접 표시
- [x] 12.3 step-by-step 진행 UX는 BriefingProgress 컴포넌트로 이전됨

## 13. 검증 및 자기 적용

- [x] 13.1 `uv run pytest tests/` 전체 통과 (322 tests)
- [x] 13.2 `cd frontend && npm run build` 성공 (270KB JS / 81KB gzip)
- [x] 13.3 CodeXray 자체 분석으로 5섹션, 바이브코딩 감지, 3축 점수(100/60/85), 타임라인 4 events 확인
- [x] 13.4 aquaview 분석으로 동일 항목 검증 (3축 53/25/0, 타임라인 1 event)
- [ ] 13.5 라이트/다크 테마 토글 브라우저 검증
- [x] 13.6 9개 미시 분석 탭 렌더링 (curl + 자동 테스트)
- [ ] 13.7 Review 탭 브라우저 명시 실행/취소/완료 흐름 검증
- [x] 13.8 `docs/validation/briefing-rebuild-self.md` 와 `docs/validation/briefing-rebuild-aquaview.md` 작성

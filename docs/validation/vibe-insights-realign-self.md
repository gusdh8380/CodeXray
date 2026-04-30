# vibe-insights-realign — 자기 적용 검증

**날짜**: 2026-05-01
**대상**: CodeXray 자체 분석

## 검증 범위

이 변경은 axes.py 3축 재설계, 점수 → 4단계 상태, 카드 수 동적 0-3, blind spot 상시 노출, ai_prompt 라벨 v7, 평가 철학 토글 등 *큰 폭의 페이로드·UI 동시 갱신*. 자기 적용 + 사용자 직접 시각 확인.

## 자동 검증

- `uv run pytest tests/ -q` → **309 passed**
- `cd frontend && npm run build` → 385KB JS / 38KB CSS 정상 생성 (이전 372KB 대비 +13KB, 새 컴포넌트 3개 + 토글 콘텐츠)
- `openspec validate vibe-insights-realign --strict` → 통과
- ruff: ai_briefing.py 의 prompt 템플릿 f-string 18 E501 (프로젝트 관행상 수용). 신규 axes.py / briefing_payload.py / 새 컴포넌트 모두 깨끗.

## 사용자 직접 시각 검증

서버 재시작 + 브라우저 하드 리프레시 후 사용자가 직접 분석을 돌렸고 다음 평가:

> "이전보다는 좋아졌다."

확인된 항목:
- 3축 (의도 / 검증 / 이어받기) 4단계 상태 라벨 표시 정상
- 신호 개수 + 대표 근거 노출
- "이 도구가 못 보는 것" 고정 블록 4 항목 노출
- "이 도구가 바이브코딩을 어떻게 평가하나요?" 토글 펼침 정상 (8 섹션)
- process proxies 보조 패널 (collapsable) — `참고용 — 단독 판정 근거 아님` 명시
- Next Actions 카드는 새 9 룰 엔진으로 합성된 vibe_coding 카드 노출

## 한계 — 다음 변경 후보

- **임계값 조정 필요 가능성**: `strong ≥ 70%` 기준이 너무 엄격해 모든 레포가 `moderate` 로 몰릴 가능성. 자기 적용 1 회만으로는 데이터 부족 — 여러 레포 분석 후 조정.
- **Non-ROBOCO 레포 검증 미실행**: 일반 OSS 레포(vite, fastapi, ruff 등) 로 편향 검증을 별도 진행 필요. 이번 archive 후 후속 작업.
- **README purpose 휴리스틱 정밀도**: 키워드 매칭 + 단락 길이만으로 *의도가 진짜 담겼는지* 못 봄 — 향후 AI 보조 검증 도입 검토.
- **Phase 1 에서 미해결 코드 측면 카드 정책**: 현재 AI 가 code/structural 카드를 카테고리별 ≤ 3 개씩 자체 처리. 전체 카드 cap (0-3 total) 정책은 미적용 — 자기 적용 데이터 보고 별도 변경에서 정리.

## 결론

본 변경의 핵심 가치(페르소나 정렬·신호 풀 일반화·4단계 상태·blind spot·평가 철학 투명성) 모두 작동. 사용자 직접 평가 *이전보다 좋아짐*. archive 가능.

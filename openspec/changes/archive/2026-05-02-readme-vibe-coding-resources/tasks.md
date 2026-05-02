## 1. 자료 셋 확인

- [x] 1.1 `frontend/src/components/briefing/EvaluationPhilosophyToggle.tsx` 의 Section 8 ("평가 기준의 출처") 자료 목록 확인
- [x] 1.2 README 에 옮길 자료 8–10 개 선정 (저자 + 저작명 + 한 줄 요약 + 링크)

## 2. README 갱신

- [x] 2.1 `README.md` 에 "Vibe Coding 처음 시작하기" 섹션 추가 (위치: README 끝부분 — 설치·실행·이해 흐름 다음)
- [x] 2.2 자료 8–10 개를 *제목 + 한 줄 요약 + 링크* 형식으로 나열
- [x] 2.3 섹션 도입부에 *"이 도구는 vibe coding 진단을 도울 뿐, vibe coding 자체를 배우려면 아래 자료부터"* 같은 한 문장 안내 추가
- [x] 2.4 링크가 모두 유효한지 수동 점검 (브라우저 클릭)

## 3. 검증 + 문서화

- [x] 3.1 README 가 markdown 으로 정상 렌더링되는지 점검 (GitHub 미리보기 또는 로컬 viewer)
- [x] 3.2 EvaluationPhilosophyToggle 의 Section 8 과 README 자료 셋이 *동일* 한지 (저자/저작 단위) 검증
- [x] 3.3 `openspec validate readme-vibe-coding-resources --strict` 통과
- [x] 3.4 CLAUDE.md "Current Sprint" 갱신
- [x] 3.5 git commit (atomic 단위)

## 4. Archive

- [x] 4.1 `openspec archive readme-vibe-coding-resources`
- [x] 4.2 archive 후 main spec 동기화 확인 — vibe-coding-insights 에 ADDED 1 개 반영

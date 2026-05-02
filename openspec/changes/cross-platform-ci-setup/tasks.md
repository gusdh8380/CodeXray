## 1. CI workflow 작성

- [ ] 1.1 `.github/workflows/ci.yml` 신규 — 3 OS matrix (`ubuntu-latest`, `macos-latest`, `windows-latest`) + Python 3.14 + uv setup + pytest
- [ ] 1.2 trigger 설정 — `push` (main branch) + `pull_request`
- [ ] 1.3 workflow 가 minimal (cache 등 부가 기능 없음) 인지 확인 — 첫 단계는 *돌리는 게 우선*

## 2. 첫 push + 결과 분석

- [ ] 2.1 commit + push → GitHub Actions 첫 실행
- [ ] 2.2 CI 결과 확인 (5–10 분 소요)
- [ ] 2.3 macOS job 통과 확인 (dev 환경과 거의 같으므로 통과 예상)
- [ ] 2.4 Linux (ubuntu) job 결과 분석 — 깨진 것 있으면 Linux fix 후보 식별
- [ ] 2.5 Windows job 결과 분석 — 깨진 테스트 / 깨진 모듈 / 인코딩·subprocess 이슈 식별

## 3. 호환성 fix 사이클

- [ ] 3.1 발견된 fix 후보별로 추측 fix 작성 (subprocess 호출 / encoding 명시 / pathlib 보강 등)
- [ ] 3.2 commit + push → CI 재실행
- [ ] 3.3 결과 확인 — 통과 / 새로운 실패 발견
- [ ] 3.4 사이클 반복 — 모든 OS 통과까지 (예상 1–2 사이클)
- [ ] 3.5 사이클 횟수가 3 회를 넘기면 *발견된 fix 만 적용 + 미해결 항목은 후속 변경* 으로 분리 — 사용자와 결정

## 4. 검증 + 문서화

- [ ] 4.1 모든 OS job *Passed* 캡처 (스크린샷 또는 CI URL)
- [ ] 4.2 `docs/validation/cross-platform-ci-setup-results.md` 작성 — 각 사이클별 발견된 fix / 추측의 적중률 / 최종 통과 기록
- [ ] 4.3 README 에 CI status badge 추가 (선택)
- [ ] 4.4 `uv run pytest tests/ -q` 로컬 macOS 통과 (회귀 없음)
- [ ] 4.5 `openspec validate cross-platform-ci-setup --strict` 통과
- [ ] 4.6 CLAUDE.md "Current Sprint" 갱신 — 본 변경 결과 + 후속 (`pypi-distribution`) 진입 가능 명시
- [ ] 4.7 git commit (atomic 단위)

## 5. Archive

- [ ] 5.1 `openspec archive cross-platform-ci-setup`
- [ ] 5.2 archive 후 main spec 동기화 확인 — web-ui 에 ADDED 1 개 반영

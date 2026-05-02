# cross-platform-ci-setup — 결과 문서

**날짜**: 2026-05-02
**대상**: GitHub Actions OS matrix CI (`ubuntu-latest` + `macos-latest` + `windows-latest`)
**목적**: 사용자 페르소나 1순위 (전부 Windows) 의 동작 보장 게이트 확립

## 1. CI 결과

| OS | 결과 | 소요 시간 |
|---|---|---|
| ubuntu-latest | ✅ 통과 | 12s |
| macos-latest | ✅ 통과 | 26s |
| windows-latest | ✅ 통과 | 44s |

전체 run: <https://github.com/gusdh8380/CodeXray/actions/runs/25249849774>

## 2. fix 사이클

### 사이클 1 — 첫 push, 모든 OS 동일 실패

run: <https://github.com/gusdh8380/CodeXray/actions/runs/25249764005>

발견된 실패: 1 개 (3 OS 동일)
```
FAILED tests/test_web_ui.py::test_main_page_serves_react_spa_when_dist_exists
  assert response.status_code == 200
  E       assert 404 == 200
```

**원인**: 테스트 이름은 `when_dist_exists` 로 *조건부* 를 시사하지만 본문은 무조건 assert. `frontend/dist/index.html` 가 없는 CI 환경 (npm build 안 함) 에서 SPA 라우트가 404 반환 → 테스트 실패.

**fix**: `pytest.mark.skipif` 로 `frontend/dist/index.html` 부재 시 skip 처리. 테스트 의도 (이름) 와 실제 동작 일치.

```python
_FRONTEND_DIST = Path(__file__).resolve().parent.parent / "frontend" / "dist" / "index.html"

@pytest.mark.skipif(
    not _FRONTEND_DIST.exists(),
    reason="frontend/dist 가 없으면 SPA 라우트도 비활성. cross-platform CI 에서 npm build 생략",
)
def test_main_page_serves_react_spa_when_dist_exists() -> None:
    ...
```

### 사이클 2 — fix 적용 후 모든 OS 통과

run: <https://github.com/gusdh8380/CodeXray/actions/runs/25249849774>

3 OS 동시 통과. Windows 호환성 추가 fix 불필요 — *예상보다 깔끔한 결과*.

## 3. 추측의 적중률

본 변경의 design.md Risk 섹션에서 언급한 *Windows-specific 깨짐 후보*:
- subprocess shell 호출 → **깨짐 없음**
- 한국어 인코딩 (cp949) → **깨짐 없음** (코드가 이미 모든 `read_text` / `write_text` 에 `encoding="utf-8"` 명시)
- pathlib OS 별 동작 → **깨짐 없음** (모든 경로 처리가 `Path` 객체 기반)
- typer / rich 색상 출력 → **깨짐 없음** (CI 에서는 색상 비활성)

→ Windows 호환성이 *이미 잘 갖춰져 있던 결과*. 추측 fix 사이클이 1 회로 끝남.

실제 깨진 원인은 *Windows-specific 가 아니라* `frontend/dist` 부재 — *모든 CI 환경* 의 공통 이슈. 사실 이 테스트는 이전부터 잠재적 위험이었음 (dev 머신에 dist 가 우연히 있어서 안 깨졌을 뿐).

## 4. 부산물

본 변경 중 *작업과 무관하게* 발견된 사실:
- `actions/checkout@v4` 와 `astral-sh/setup-uv@v6` 가 Node.js 20 사용 → 2026-06-02 까지 v5 (또는 Node 24 호환 버전) 으로 업그레이드 필요. 본 변경 범위 밖, 후속 정리.

## 5. 자동 검증

- pytest 로컬 (macOS): **320 passed** (변경 전 동일)
- CI 3 OS 통과 (위 §1 표)
- `openspec validate cross-platform-ci-setup --strict` 통과

## 6. 한계

- frontend `npm run build` CI 미포함 — 별도 변경 `frontend-ci` 후보
- E2E (codexray serve 실제 동작) 미검증 — 동료 베타 단계로 미룸
- Python 3.14 단일 버전만 검증 — 3.12 / 3.13 matrix 추가는 후속

## 7. 결론

본 변경의 핵심 가치 — *"Windows 동작 보장 게이트 확립"* — 검증됨. 사이클 1 회로 모든 OS 통과, Windows 호환성 추가 fix 불필요. 다음 변경 `pypi-distribution` 진입 가능. archive.

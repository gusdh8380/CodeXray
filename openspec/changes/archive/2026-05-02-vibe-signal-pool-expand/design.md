## Context

`non-roboco-validation` 검증에서 신호 풀의 ROBOCO 편향이 직접 입증됐다. 자기 적용은 100%/100%/100%, 외부 OSS 는 weak 으로 몰림. 사용자가 옵션 A' 채택 후 (vibe-detection-rebalance 에서 detection 게이트는 유지하기로 결정), 본 변경은 게이트 통과한 외부 OSS 의 *평가 정확도* 를 끌어올리는 게 목적. *임계값 비율 / 상태 매핑 / 카드 합성* 은 의도적으로 건드리지 않음.

## Goals / Non-Goals

**Goals:**
- 의도 / 검증 / 이어받기 축의 신호 풀에 일반 OSS 관행 추가.
- 새 신호는 *명백히 잘된 프로젝트* 가 가지는 흔적만 (false positive 회피).
- 자기 적용 회귀 0 (이미 strong 100% 인 자기 결과 바뀌지 않음).
- non-roboco-validation 데이터 재분석으로 효과 입증 (weak 빈도 감소 확인).

**Non-Goals:**
- 임계값 (70/40/10) 변경. 후속 변경 `vibe-thresholds-tune` 으로.
- 4 단계 상태 매핑 변경.
- 카드 합성 9 룰 변경.
- detection 게이트 변경 (이미 vibe-detection-rebalance 에서 결정).
- 기존 신호 검증 로직 (regex / 파일 존재 패턴) 의 재구조화. 새 후보를 같은 패턴으로 추가만.

## Decisions

### 결정 1: pyproject/package.json description 충실도 임계 — 길이 ≥ 30 자 또는 keywords 동봉

빈 description 도 잡히면 false positive. 일정 길이 + 의미 있는 컨텍스트 신호 (keywords) 가 있어야 *진짜 의도가 적힌 거* 로 인정.

```python
# 의사 코드
desc = pyproject.get("project", {}).get("description", "")
keywords = pyproject.get("project", {}).get("keywords", [])
if len(desc) >= 30 or (desc and len(keywords) > 0):
    found.append("pyproject.toml description")
```

**대안 — 단순 존재만 확인**: description 한 글자도 통과. fastapi 가 30 자 이상 description 가지므로 잡힘 OK 지만 텅 빈 프로젝트도 잡힘. 기각.

**대안 — 길이 ≥ 100 자 같은 더 엄격**: 너무 빡빡. 일반 OSS 의 description 평균 30–80 자. 30 자 채택.

### 결정 2: README 명시 섹션 헤더 매칭은 `_has_purpose_paragraph` 보조

기존 `_has_purpose_paragraph` 는 첫 5 단락 키워드 매칭. 이건 유지. 추가로 *명시 섹션 헤더* (`## What`, `## Why`, `## Purpose`, `## About` 한국어 포함) 가 README *어디에든* 있으면 통과. 이게 더 강한 신호 (작성자가 *섹션 제목* 까지 의도해서 적은 것).

```python
def _has_purpose_paragraph(readme_text: str) -> bool:
    if not readme_text or len(readme_text) < 200:
        return False
    # 기존: 첫 5 단락 키워드
    paras = [p.strip() for p in readme_text.split("\n\n") if p.strip()][:5]
    head = "\n".join(paras).lower()
    if any(kw.lower() in head for kw in _PURPOSE_KEYWORDS):
        return True
    # 추가: 명시 섹션 헤더
    if re.search(
        r"^##+\s*(What|Why|Purpose|About|이 프로젝트|정체|역할)",
        readme_text,
        re.MULTILINE | re.IGNORECASE,
    ):
        return True
    return False
```

### 결정 3: examples/ 같은 디렉토리는 *비어있지 않을 때만* 인정

`examples/` 빈 폴더는 false positive. *최소 1 개 파일* 있어야 인정. `_check_manual_validation` 에 디렉토리 비어있지 않음 가드 추가.

```python
def _dir_nonempty(root: Path, path: str) -> bool:
    p = root / path
    if not p.exists() or not p.is_dir():
        return False
    try:
        return any(p.iterdir())
    except OSError:
        return False
```

### 결정 4: handoff 신호 풀 확장 — `_check_handoff_doc` 만 손댐

`_check_continuity_*` 는 이미 git history 기반 + saved plans 다 보고 있음. handoff 가 가장 좁은 풀이라 여기에 후보 추가가 가성비 최고.

`MAINTAINERS.md`, `MAINTAINERS` (확장자 없음), `CODEOWNERS`, `.github/CODEOWNERS`, `docs/getting-started/`, `docs/onboarding/`, `docs/contributing/` 추가.

### 결정 5: 회귀 점검 절차

자기 적용 결과 비교:
- 변경 전: CodeXray 의도/검증/이어받기 모두 strong 3/3 (100%)
- 변경 후: 같아야 함. 만약 신호 카운트가 늘어나면 (예: pyproject description 추가로 의도 4/4 같이 — 단 풀 크기도 같이 늘어 ratio 100% 유지) OK. 카운트가 줄어들면 *회귀* — 점검 필요.

외부 OSS 9 개 재분석:
- non-roboco-validation 의 raw 데이터와 비교
- weak 가 moderate 로 올라가는 케이스 기록
- 임계값 (70/40/10) 자체는 안 바뀌므로 strong 으로 점프하는 케이스는 적을 것

## Risks / Trade-offs

- [신호 풀 늘면 모든 축이 strong 으로 몰릴 위험] → 풀 크기 (`signal_pool_size`) 도 같이 늘어 ratio 가 같이 조정되므로 자동 보정. 다만 *이미 strong 인 레포가 더 강해지는* 것은 OK (의도된 효과).
- [pyproject description 1 줄에 false positive] → 길이 임계 30 자 + keywords 보조로 차단 (결정 1).
- [examples/ 디렉토리 빈 채로 통과] → 비어있지 않음 가드 (결정 3).
- [README 헤더 매칭이 *코드 블록 안의 ## What* 까지 잡음] → re.MULTILINE 만 쓰고 코드 블록 제외 안 함. 하지만 `## What` 같은 헤더가 코드 블록 안에 들어갈 일은 거의 없음 (실제 README 패턴 보면 OK). 위험 무시.

## Migration Plan

1. axes.py 변경 (신호 함수 3 개 보강 + 헬퍼 1–2 개 추가).
2. 단위 테스트 추가 — 새 신호 잡힘 + 임계 미달 시 안 잡힘 케이스.
3. `uv run pytest tests/ -q` 통과.
4. 자기 적용 회귀 점검 — `validate_external_repos.py` 로 CodeXray 결과 수집, 변경 전 데이터 (`docs/validation/non-roboco-data/CodeXray.json`) 와 byte-level 비교 또는 ratio 동일 확인.
5. 9 외부 OSS 재분석 — 새 데이터 `docs/validation/non-roboco-data/` 갱신, 결과 문서 작성.
6. 캐시 / SCHEMA_VERSION bump 불필요 (응답 형태 동일).

롤백: 단순 — git revert 후 axes.py 만 원상복귀.

## Open Questions

- 새 신호 추가 후 자기 적용에서 풀 크기가 늘어나면서 ratio 가 살짝 떨어질 가능성. 예: 의도 풀 크기 3 → 4 (pyproject description 추가) 인데 자기 프로젝트가 그 신호도 만족하면 4/4 = 100% 유지. 만약 자기 프로젝트가 새 신호 *못* 만족하면 4/3 → 3/4 = 75% — 여전히 strong 임계 70% 통과. 큰 문제 없음. 점검 필요.
- pyproject description 길이 임계 30 자가 적정한지 — 9 외부 OSS 의 실제 description 길이 분포로 사후 검증.

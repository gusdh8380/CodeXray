## Why

`non-roboco-validation` 결과 문서 §5.2 가 신호 풀 추가 후보를 데이터 기반으로 정리했다. 자기 적용에서 CodeXray 가 100%/100%/100% 인 게 *신호 풀이 ROBOCO/OMC 컨벤션에 과적합* 의 직접 증거. 외부 OSS 케이스에서 의도/검증/이어받기 좋은 관행을 가진 레포가 우리 신호 풀에 안 맞아 weak 으로 잡힌 사례가 다수다 (예: OpenSpec 의도 weak — `pyproject` description / `MAINTAINERS` 같은 일반 OSS 신호를 못 잡음).

본 변경은 신호 풀을 *AI 도구 컨벤션 위주에서 일반 OSS 관행까지* 확장한다. 임계값·상태 매핑·카드 합성 로직은 건드리지 않고 *신호가 무엇을 보는가* 만 넓힌다.

## What Changes

- **의도 축 — 프로젝트 의도 문서 신호 풀 확장**:
  - `pyproject.toml` 의 `description` (충실도: 길이 ≥ 30 자 또는 `keywords` 동봉)
  - `package.json` 의 `description` (같은 휴리스틱)
  - README 의 `## What`, `## Why`, `## Purpose`, `## About` 명시 섹션 헤더 매칭 추가 (현재는 첫 5 단락 키워드 매칭만)
- **검증 축 — 손 검증 흔적 신호 풀 확장**:
  - `examples/`, `demo/`, `samples/`, `examples-*/` 디렉토리 (코드 demo 도 손 검증의 한 형태)
  - `.storybook/` (UI 손 검증)
- **이어받기 축 — 핸드오프 문서 신호 풀 확장**:
  - `MAINTAINERS.md`, `MAINTAINERS`, `CODEOWNERS`, `.github/CODEOWNERS`
  - `docs/getting-started/`, `docs/onboarding/`, `docs/contributing/`
- 신호별 단위 테스트 추가 (각 신호가 잡힘 / 안 잡힘 케이스).
- 검증 문서 `docs/validation/vibe-signal-pool-expand-results.md` — 9 외부 OSS 재분석 pre/post 비교.

원칙:
- 새 신호는 *AI 도구 컨벤션이 아닌 일반 OSS 관행* 위주
- 임계값 / 4 단계 상태 매핑 / 카드 합성 로직 *변경 안 함* — 신호 풀 확장만
- 자기 적용 (CodeXray 자체) 결과 회귀 없음 (이미 모두 잡히던 신호라 영향 없어야 함)

## Capabilities

### New Capabilities
없음.

### Modified Capabilities
- `vibe-coding-insights`: "3축 진단 평가" 의 axis 평가 시나리오 + "8 운영 정의와 측정 가능성 분리" 의 흔적 기반 6 신호 정의를 *broadened 풀 명시* 로 갱신. 신호 항목 자체는 동일 (예: "프로젝트 의도 문서 1종 이상"), 그 안에 어떤 패턴이 들어가는지가 늘어남.

## Impact

- **변경 영향 코드**: `src/codexray/vibe_insights/axes.py` (신호 검사 함수 6 개 중 3 개 확장), `tests/test_vibe_insights.py` (신규 단위 테스트)
- **테스트**: 312 → 318 정도 (신호별 +1 테스트씩)
- **회귀 점검**: 자기 적용 (CodeXray) + non-roboco-validation 의 9 외부 OSS 재분석으로 *weak 가 줄어드는지* 확인
- **PROMPT_VERSION/SCHEMA_VERSION**: bump 불필요 (응답 형태 동일, 신호 검출 결과만 변경)
- **사용자 가시 변화**: 외부 OSS 분석 시 의도/검증/이어받기 점수가 더 정확해짐. 예: fastapi 가 detection 통과한다면 의도 weak → moderate 또는 strong 으로 올라갈 가능성. 단 fastapi 는 여전히 detection 게이트에서 떨어지므로 본 변경의 직접 수혜는 *AI 도구 도입한 일반 OSS* 가 됨.

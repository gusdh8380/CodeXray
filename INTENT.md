# CodeXray

> 임의의 코드베이스를 입력하면 구조를 시각화하고 품질을 평가하여,
> "다음에 무엇을 할지"의 근거를 제공한다.

## MVP at a glance
- **Inputs**: 로컬 디렉토리 / Git URL / 압축 파일
- **Outputs**: 1페이지 리포트 + 인터랙티브 대시보드 + JSON
- **Core**: 구조 분석 · 정량 평가(A~F) · AI 정성 평가 · 핫스팟 매트릭스
- **Constraint**: 로컬 실행 우선, AI 평가는 opt-in
- **Top risk**: AI 평가 부정확 → 모든 평가에 근거 라인 인용 필수
- **First validation**: 사용자 본인의 작은 게임 프로젝트로 dogfood

## Planning docs
- `docs/vision.md` — 비전 + 대상 사용자 + 핵심 문제
- `docs/intent.md` — MVP 기능 + 비목표 + 성공 기준
- `docs/constraints.md` — 원칙 + 리스크 + 1차 검증 대상

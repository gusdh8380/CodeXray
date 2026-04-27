# Draft proposal — `add-inventory-cli`

> 첫 단추. 코드베이스 입력 → 한 표(언어/파일 수/LoC/최종 수정일) 출력.
> MVP 기능 #1(구조 분석)의 가장 작은 단위.

## /opsx:propose payload (복사해서 붙여넣기)

```
add-inventory-cli: 코드베이스 입력을 받아 인벤토리 한 표를 stdout으로 출력하는 최소 CLI.

Why
- MVP 모든 기능은 "코드베이스 입력 → 분석 결과"의 변형. 가장 작은 입력→출력 한 사이클을
  먼저 만들어야 이후의 의존성 그래프, 정량 평가, AI 평가가 같은 입력 인터페이스 위에 쌓인다.

What changes
- CLI 진입점 1개: `codexray inventory <path>`
- 입력: 로컬 디렉토리 경로 1개만 (Git URL, 압축은 다음 변경)
- 출력: 표 1개 — 언어 / 파일 수 / LoC / 가장 최근 수정일
- 언어 감지: 확장자 기반 단순 매핑 (Python, JS, TS, Java, C# 우선)
- 무시 규칙: .gitignore + 기본(node_modules, .git, dist, build, venv)

Non-goals
- 의존성 그래프 / 호출 관계 / 진입점 식별
- AI 평가
- Git URL / 압축 입력
- 멀티 출력 포맷 (JSON, Markdown 리포트)

Validation target
- 사용자의 작은 게임 프로젝트에 대해 5초 내 표 출력
```

## 왜 이게 첫 변경인가
- 입력 처리 + 파일 워킹 + 언어 분류 — 이후 모든 분석의 기반.
- AI 의존 없음 → 결정론적, 회귀 검증 쉬움.
- 사용자의 "작은 게임 프로젝트" dogfood로 5분 내 검증 가능.

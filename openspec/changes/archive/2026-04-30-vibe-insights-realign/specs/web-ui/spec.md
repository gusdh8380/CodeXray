## ADDED Requirements

### Requirement: 4단계 축 상태 표시
The web UI SHALL render each vibe coding axis (`intent / verification / continuity`) as a 4-level state label with a recognized-signal count and 2–3 representative pieces of evidence, instead of a 0–100 numeric score.

#### Scenario: 상태 라벨 표시
- **WHEN** vibe coding 섹션이 렌더링되면
- **THEN** 각 축은 다음 중 하나의 상태 라벨로 표시된다: 강함 (`strong`), 보통 (`moderate`), 약함 (`weak`), 판단유보 (`unknown`)

#### Scenario: 근거 개수와 대표 근거
- **WHEN** 축 상태 라벨이 표시되면
- **THEN** 그 옆에 인지된 신호 개수(예: "신호 4개") 와 대표 근거 2-3 개(파일 경로 또는 문서 라벨)가 함께 표시된다

#### Scenario: 0-100 점수 미노출
- **WHEN** 브리핑 영역이 렌더링되면
- **THEN** 0-100 원시 점수는 *기본 노출되지 않으며*, 디버그/실험 토글이 있는 경우에만 그 안에서 보인다

### Requirement: 다음 행동 카드 0–3개 동적 렌더링
The web UI SHALL render between 0 and 3 next-action cards based on the payload's `next_actions` length, and display the corresponding zero-action message (`praise / judgment_pending / silent`) when the list is empty.

#### Scenario: 카드 0개 + 칭찬
- **WHEN** payload 의 `next_actions` 가 빈 리스트이고 zero-action 분기가 `praise` 일 때
- **THEN** UI 는 다음 행동 카드 영역을 숨기지 않고, 대신 "유지할 습관" 한 줄 메시지를 같은 카드 자리에 보조 톤으로 표시한다

#### Scenario: 카드 0개 + 판단 보류
- **WHEN** payload 의 `next_actions` 가 빈 리스트이고 zero-action 분기가 `judgment_pending` 일 때
- **THEN** UI 는 "코드만 봐선 추가 진단 어려움 — 사용자 대화·시연이 필요합니다" 메시지를 표시하고 칭찬 톤은 사용하지 않는다

#### Scenario: 카드 0개 + 침묵
- **WHEN** payload 의 `next_actions` 가 빈 리스트이고 zero-action 분기가 `silent` 일 때
- **THEN** UI 는 다음 행동 영역에 별도 카드나 메시지를 표시하지 않는다 (영역 자체를 숨김 또는 보조 텍스트만 노출)

#### Scenario: 카드 1-3개
- **WHEN** payload 의 `next_actions` 가 1-3 개 항목을 포함하면
- **THEN** UI 는 그 만큼의 카드를 카테고리 그룹과 함께 렌더링한다 (직전 변경의 카테고리 표시 유지)

### Requirement: blind spot 고정 블록 UI
The web UI SHALL display a fixed "이 도구가 못 본 것" block in the Briefing area on every analysis result page, regardless of axis states or card counts.

#### Scenario: 블록 위치
- **WHEN** Briefing 화면이 렌더링되면
- **THEN** 검토 경고 배너 바로 아래 또는 vibe coding 섹션 하단에 blind spot 블록이 표시된다

#### Scenario: 블록 내용
- **WHEN** blind spot 블록이 렌더링되면
- **THEN** 다음 4 항목이 최소한 포함되고, codebase-briefing 의 "blind spot 상시 노출" 요구사항과 일치한다:
  1. 사용자(나)가 What/Why/Next 를 자기 입으로 설명할 수 있는가
  2. 손으로 한 검증이 *실제로 매번* 굴러가는가
  3. 다음 행동의 우선순위를 사람이 정하고 있는가
  4. 외부 도구(Notion, Confluence, Slack, Linear 등)에 있는 의도·결정 흔적과 README 같은 문서의 *질적 깊이* 는 자동 판단 못 합니다

#### Scenario: 블록 톤은 자가 점검
- **WHEN** blind spot 블록이 렌더링되면
- **THEN** 본문 톤은 *자가 점검 체크리스트* 이며 "이 도구가 못 미덥다" 인상이 아닌 *사용자 책임 환기* 표현을 사용한다

### Requirement: 평가 철학 토글
The web UI SHALL display a collapsible "이 도구가 바이브코딩을 어떻게 평가하나요?" toggle at the bottom of the Briefing area, defaulting to collapsed, that exposes the evaluation philosophy and methodology to the user when expanded.

#### Scenario: 토글 위치와 기본 상태
- **WHEN** Briefing 화면이 렌더링되면
- **THEN** vibe coding 섹션 최하단 (blind spot 블록 아래) 또는 Briefing 화면 footer 영역에 "이 도구가 바이브코딩을 어떻게 평가하나요?" 라벨의 토글이 표시되고, 기본 상태는 *접힘* 이다

#### Scenario: 펼침 콘텐츠 구조
- **WHEN** 사용자가 토글을 펼치면
- **THEN** 다음 8 섹션이 순서대로 노출된다:
  1. 슬로건 한 줄 — "주인이 있는 프로젝트"
  2. 운영 정의 3 구조 — 외부화된 의도 / 독립 검증 / 인간 최종 판단
  3. 8 운영 신호 — 흔적 6 + 사각지대 2
  4. 3축 매핑 — 어느 신호가 어느 축에 매핑되는지
  5. 4 단계 상태 의미 — strong / moderate / weak / unknown 각각의 뜻과 임계
  6. 카드 수 정책 — 왜 0-3 동적인가
  7. 사각지대 4 항목 재명시
  8. 출처 — 리서치에서 인용한 핵심 자료

#### Scenario: 토글은 모든 화면에 일관되게 노출
- **WHEN** 사용자가 분석 결과를 새로 받거나 같은 결과를 다시 볼 때
- **THEN** 토글의 *콘텐츠는 동일하게* 표시된다 (분석 결과에 따라 변하지 않음 — 평가 *방법론* 자체이므로)

#### Scenario: 토글 콘텐츠 톤
- **WHEN** 토글 콘텐츠가 렌더링되면
- **THEN** 본문은 비개발자 100% 청자 톤을 유지하며 (codebase-briefing 의 "Plain-language technical translation" 요구사항 준수), 출처 인용은 영어 원문 그대로 OK

### Requirement: 약한 process proxy 보조 패널 분리
The web UI SHALL display weak process proxies (feat/fix ratio, spec commit timing, hotspot accumulation) only in a clearly separated supplementary panel, not as primary axis evidence.

#### Scenario: 보조 정보 패널 분리
- **WHEN** payload 의 `process_proxies` 필드가 비어있지 않을 때
- **THEN** UI 는 그 정보를 vibe coding 섹션의 *축 상태 라벨 옆* 이 아니라 *별도 보조 패널* (collapsable 토글 또는 작은 글씨 보조 라인) 로 노출한다

#### Scenario: 보조 패널 라벨
- **WHEN** 보조 패널이 렌더링되면
- **THEN** 패널의 헤더는 명확하게 "참고용 — 단독 판정 근거 아님" 같은 표현을 포함하여 사용자가 이를 *축 상태와 별개* 로 인식하게 한다

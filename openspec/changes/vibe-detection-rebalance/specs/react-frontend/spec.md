## MODIFIED Requirements

### Requirement: Briefing 매크로 화면 4–5개 섹션
The system SHALL render the Briefing screen as four to five vertically-flowing sections optimized for first-time understanding and live presentation, where the vibe coding insights section is *conditionally rendered* based on detection.

#### Scenario: 섹션 순서와 정체성 — 감지 시 5개
- **WHEN** Briefing 결과가 표시되고 vibe coding 이 *감지된* 경우
- **THEN** 화면은 위에서 아래로 "이게 뭐야 / 어떻게 만들어졌나 / 지금 상태 / 바이브코딩 인사이트 / 지금 뭘 해야 해" 순서로 다섯 섹션을 표시한다

#### Scenario: 섹션 순서와 정체성 — 비감지 시 4개
- **WHEN** Briefing 결과가 표시되고 vibe coding 이 *감지되지 않은* 경우 (응답에 `vibe_insights` 가 부재 또는 null)
- **THEN** 화면은 위에서 아래로 "이게 뭐야 / 어떻게 만들어졌나 / 지금 상태 / 지금 뭘 해야 해" 순서로 네 섹션만 표시한다. 바이브코딩 인사이트 섹션은 렌더링되지 않으며 시작 가이드 같은 대체 콘텐츠도 노출되지 않는다

#### Scenario: 섹션별 미시 탭 링크
- **WHEN** "어떻게 만들어졌나" 섹션이 표시되면
- **THEN** 섹션은 Graph 탭으로 이동하는 링크를 포함하고, "지금 상태" 섹션은 Quality 탭, 위험 위치는 Hotspots 탭으로 이동하는 링크를 포함한다

#### Scenario: 발표 친화적 시각
- **WHEN** Briefing 결과가 표시되면
- **THEN** 큰 제목, 충분한 여백, 한국어 본문 폰트로 발표용 화면 그대로 사용 가능한 시각 품질을 갖춘다

## ADDED Requirements

### Requirement: VibeInsightsSection 의 조건부 렌더링
The frontend SHALL render the `VibeInsightsSection` component *only when* `data.vibe_insights` is present and truthy. When the field is absent or null (non-detected projects), the section is skipped entirely with no placeholder, no "not detected" message, and no starter-guide alternative.

#### Scenario: vibe_insights 부재 시 컴포넌트 호출 자체 생략
- **WHEN** `BriefingScreen` 의 데이터에서 `data.vibe_insights` 가 부재이거나 null/falsy 일 때
- **THEN** `<VibeInsightsSection />` 컴포넌트는 *호출되지 않으며* DOM 에 어떤 흔적도 남기지 않는다 (placeholder 없음, "비감지" 텍스트 없음, starter guide 영역 없음)

#### Scenario: vibe_insights 존재 시 정상 렌더링
- **WHEN** `data.vibe_insights` 가 truthy 객체이고 `detected: true` 일 때
- **THEN** `<VibeInsightsSection />` 가 정상 렌더링되고 3 축 카드 / blind spot / process proxies / 평가 철학 토글이 모두 노출된다

#### Scenario: VibeInsightsSection 내부에 비감지 분기 없음
- **WHEN** `VibeInsightsSection` 의 구현이 검사되면
- **THEN** 컴포넌트는 `detected: false` 분기 / StarterGuide 컴포넌트 / StarterGuideCard 컴포넌트 / CopyPromptBox (시작 가이드용) 를 *포함하지 않는다*. 컴포넌트는 항상 detected=true 데이터만 받는다고 가정한다

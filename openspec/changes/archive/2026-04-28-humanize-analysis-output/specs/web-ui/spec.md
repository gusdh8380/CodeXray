## ADDED Requirements

### Requirement: LoC 규모 레이블
The system SHALL display LoC values with a human-readable size label.

#### Scenario: LoC 표시
- **WHEN** Inventory 또는 Overview에서 LoC 수치가 표시되면
- **THEN** 숫자 옆에 규모 레이블(소규모/중규모/대규모/초대형)이 함께 표시된다

### Requirement: Coupling 위험도 표시
The system SHALL display coupling values with a risk level label.

#### Scenario: Coupling 수치 표시
- **WHEN** Metrics 또는 Hotspots 탭에서 coupling 수치가 표시되면
- **THEN** 수치 옆에 위험도 레이블(낮음/보통/높음/매우높음)이 함께 표시된다

### Requirement: 전문 용어 설명
The system SHALL display explanatory context next to technical terms.

#### Scenario: fan-in/fan-out 용어 표시
- **WHEN** Metrics 탭 컬럼 헤더에 fan-in/fan-out이 표시되면
- **THEN** 괄호 안에 짧은 설명(이 파일에 의존하는 수/이 파일이 의존하는 수)이 함께 표시된다

### Requirement: Hotspot 카테고리 한국어화
The system SHALL display hotspot category labels in Korean with descriptions.

#### Scenario: Hotspot 카테고리 표시
- **WHEN** Hotspots 탭에서 카테고리가 표시되면
- **THEN** 영어 코드(hotspot/active_stable/neglected_complex/stable) 대신 한국어 설명이 표시된다

### Requirement: Quality 등급 해석
The system SHALL display a one-line interpretation alongside each quality grade.

#### Scenario: Quality 등급 표시
- **WHEN** Quality 탭 또는 Overview에서 A~F 등급이 표시되면
- **THEN** 등급 옆에 한 줄 해석이 함께 표시된다

## ADDED Requirements

### Requirement: Briefing 자동 랜딩 시작
The system SHALL auto-start Briefing analysis when the page loads, making it the landing experience.

#### Scenario: 첫 분석 자동 시작
- **WHEN** 사용자가 경로를 입력하고 분석을 시작하면
- **THEN** Briefing 분석이 자동으로 실행되고 결과가 첫 화면에 표시된다

#### Scenario: Briefing 로딩 중 상태
- **WHEN** Briefing 분석이 진행 중이면
- **THEN** 결과 패널에 로딩 상태가 표시되고 빈 화면이 노출되지 않는다

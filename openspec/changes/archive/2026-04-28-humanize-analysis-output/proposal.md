## Why

분석 결과가 숫자와 전문 용어로만 표시되어, 비개발자는 물론 개발자도 "이게 좋은 건지 나쁜 건지" 직관적으로 파악하기 어렵다. "coupling=30", "avg_fan_inout=4.59", "LoC: 8808" 같은 표현은 맥락 없이 던져진 숫자일 뿐이다.

Intent "전문 용어가 나오더라도 비개발자가 맥락을 파악할 수 있다"와 "시니어 개발자도 '오, 이거 괜찮은데' 할 분석 깊이가 있다"를 달성하려면, 숫자에 의미와 규모감을 부여하고 용어에 맥락 설명을 붙여야 한다.

## What Changes

- **용어 설명 툴팁/주석**: fan-in, fan-out, coupling, LoC, SCC, hotspot 등 주요 용어 옆에 괄호 설명 추가
- **숫자 인간화**: LoC → 규모 레이블 (소규모/중규모/대규모), coupling 수치 → 위험도 레이블, 등급 → 한 줄 해석
- **Overview 카드 인간화**: "8808 LoC" → "약 8,800줄 (중간 규모)", "30 nodes/287 edges" → 의미 있는 설명
- **Quality 등급 설명**: A~F 각 등급에 "무슨 뜻인지" 한 줄 추가
- **Hotspot 카테고리 설명**: "hotspot", "neglected_complex", "active_stable" → 한국어 설명

## Capabilities

### New Capabilities
- (없음)

### Modified Capabilities
- `web-ui`: Overview, Quality, Metrics, Hotspots 탭의 숫자/용어 표현 인간화

## Impact

- `src/codexray/web/render.py` — 각 render 함수의 숫자/용어 표현 수정
- 기존 테스트 `tests/test_web_ui.py` — 변경된 텍스트 어서션 업데이트 가능성

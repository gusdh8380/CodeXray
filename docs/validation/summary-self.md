# Strengths / Weaknesses / Next Actions Validation — Self

Change: `add-strengths-weaknesses-summary`

Target: `/Users/jeonhyeono/Project/personal/CodeXray`

CLI report capture:

```text
elapsed=0.566s grade=D(56) strengths=2 weaknesses=3 actions=3
sections=## Strengths,## Weaknesses,## Next Actions
strengths=순환 의존 없음 (DAG) | test 차원 A 등급
weaknesses=documentation 차원 F 등급 | coupling 차원 D 등급 | Top hotspot 위험: src/codexray/cli.py
actions=문서화 진입점 작성 | 결합도 분해 (책임 분리) | Top hotspot에 테스트 + 책임 분리
markdown_has_evidence=True
```

Web Overview / Report capture:

```text
overview_status=200 report_status=200
overview_cards=4
report_cards=4
overview_has=True
report_has=True
```

Interpretation:

- CLI report includes `## Strengths`, `## Weaknesses`, and `## Next Actions`.
- Web Overview and Web Report both render the summary card sections.
- Runtime is below the 5 second budget.

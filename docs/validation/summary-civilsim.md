# Strengths / Weaknesses / Next Actions Validation — CivilSim

Change: `add-strengths-weaknesses-summary`

Target: `/Users/jeonhyeono/Project/personal/CivilSim`

CLI report capture:

```text
elapsed=2.234s grade=D(40) strengths=1 weaknesses=3 actions=3
sections=## Strengths,## Weaknesses,## Next Actions
strengths=cohesion 차원 A 등급
weaknesses=test 차원 F 등급 | coupling 차원 F 등급 | documentation 차원 F 등급
actions=characterization test 우선 보강 | 결합도 분해 (책임 분리) | 문서화 진입점 작성
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

- CivilSim report includes deterministic strengths, weaknesses, and next actions.
- The key risk profile is visible: test/coupling/documentation F with action mapping.
- Runtime is below the 5 second budget.

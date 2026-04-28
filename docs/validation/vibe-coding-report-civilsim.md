# Vibe Coding Report Validation — CivilSim

Change: `add-vibe-coding-report-tab`

Target: `/Users/jeonhyeono/Project/personal/CivilSim`

Command:

```bash
uv run python -c "import time; from pathlib import Path; from codexray.vibe import build_vibe_coding_report; root=Path('/Users/jeonhyeono/Project/personal/CivilSim'); t=time.perf_counter(); r=build_vibe_coding_report(root); dt=time.perf_counter()-t; print(f'elapsed={dt:.3f}s confidence={r.confidence} score={r.confidence_score} areas={len(r.process_areas)} evidence={len(r.evidence)}'); print('areas=' + ','.join(r.process_areas)); print('strengths=' + ' | '.join(x.text for x in r.strengths)); print('risks=' + ' | '.join(x.text for x in r.risks)); print('actions=' + ' | '.join(x.text for x in r.actions)); print('evidence=' + ','.join(x.path for x in r.evidence[:12]))"
```

Result:

```text
elapsed=0.496s confidence=medium score=36 areas=2 evidence=2
areas=agent_instructions,automation
strengths=에이전트가 따라야 할 작업 규칙이 레포 안에 남아 있습니다.
risks=에이전트 작업 결과를 실제 입력으로 검증한 캡처가 보이지 않습니다. | 다음 세션이 이어받을 메모리나 handoff 근거가 부족합니다. | 에이전트 지침은 있지만 변경 명세를 강제하는 흐름은 약해 보입니다.
actions=큰 변경은 OpenSpec 같은 명세 흐름으로 의도와 검증 조건을 남기세요. | 대표 입력에서 실행 결과를 docs/validation 아래에 캡처하세요. | 다음 에이전트가 이어받을 handoff와 프로젝트 메모리를 남기세요.
evidence=CLAUDE.md,.claude/settings.local.json
```

Interpretation:

- CivilSim has medium evidence of an agent-assisted environment from Claude-related artifacts.
- The report correctly identifies missing validation, handoff, and spec-workflow evidence as risks and next actions.
- Runtime is below the 5 second budget on the large Unity validation tree.

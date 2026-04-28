# Vibe Coding Report Validation — Self

Change: `add-vibe-coding-report-tab`

Target: `/Users/jeonhyeono/Project/personal/CodeXray`

Command:

```bash
uv run python -c "import time; from pathlib import Path; from codexray.vibe import build_vibe_coding_report; root=Path('.'); t=time.perf_counter(); r=build_vibe_coding_report(root); dt=time.perf_counter()-t; print(f'elapsed={dt:.3f}s confidence={r.confidence} score={r.confidence_score} areas={len(r.process_areas)} evidence={len(r.evidence)}'); print('areas=' + ','.join(r.process_areas)); print('strengths=' + ' | '.join(x.text for x in r.strengths)); print('risks=' + ' | '.join(x.text for x in r.risks)); print('actions=' + ' | '.join(x.text for x in r.actions)); print('evidence=' + ','.join(x.path for x in r.evidence[:12]))"
```

Result:

```text
elapsed=0.047s confidence=high score=100 areas=6 evidence=17
areas=agent_instructions,automation,memory_handoff,retrospectives,spec_workflow,validation
strengths=에이전트가 따라야 할 작업 규칙이 레포 안에 남아 있습니다. | 코드 전에 변경 의도와 요구사항을 남기는 명세 흐름이 보입니다. | 분석 결과를 실제 프로젝트에서 검증한 흔적이 있습니다.
risks=
actions=현재 환경을 유지하되, 새 결정은 메모리와 회고에 계속 누적하세요.
evidence=.claude/commands,.claude/skills,AGENTS.md,CLAUDE.md,.claude/settings.json,.claude/settings.local.json,.husky/pre-commit,.roboco/config.json,.omc/project-memory.json,.omc/sessions,docs/handoff-to-codex.md,docs/vibe-coding
```

Interpretation:

- Self tree has strong evidence across all six process areas.
- The report correctly recognizes the ROBOCO / OpenSpec / OMC / Claude environment created for this project.
- Runtime is well below the 5 second budget.

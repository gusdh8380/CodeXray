## Context

Presentation mode solved navigation, but not depth. Current slides combine card text into one paragraph and expose evidence. That is structurally correct but too shallow for the intended "developer made this PPT for my team" experience.

## Goals / Non-Goals

**Goals:**

- Make each slide contain a clear interpretation: what this means, why it matters, and what to do next.
- Use deterministic rules from existing analyzers rather than AI-generated prose.
- Add process interpretation from git/vibe-coding evidence.
- Make copy understandable to non-developers without removing technical evidence.

**Non-Goals:**

- PPTX/PDF export.
- New AI calls for briefing text.
- Redesigning Dashboard graph interaction.
- Changing analyzer scoring algorithms.

## Decisions

1. **Add structured slide fields instead of only longer paragraphs.**
   - Rationale: rendering can distinguish summary, meaning, risk, and action.
   - Alternative: generate a single longer narrative string. Rejected because it is harder to scan and test.

2. **Use deterministic thresholds from existing metrics.**
   - Rationale: repeatable output is a project constraint. The briefing should be stable.
   - Alternative: ask AI to write slides. Rejected for latency, variance, and evidence risk.

3. **Interpret process evidence as a creation story.**
   - Rationale: vibe-coding users care about how the repo was made, not just whether `.claude` exists.

## Risks / Trade-offs

- **[Risk] Deterministic prose can sound formulaic.** → Mitigation: write domain-specific sentence builders per slide type.
- **[Risk] More text can overload the slide.** → Mitigation: render as compact sections: Meaning, Risk, Action.
- **[Risk] Interpretation may overstate evidence.** → Mitigation: phrase claims as observed signals and cite concrete values.

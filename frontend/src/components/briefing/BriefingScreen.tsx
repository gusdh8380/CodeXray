import { SectionShell } from "./SectionShell"
import { VibeInsightsSection } from "./VibeInsightsSection"
import { NextActionsSection } from "./NextActionsSection"
import { MicroAnalysisArea } from "@/components/micro/MicroAnalysisArea"
import type { BriefingPayload } from "@/lib/api"

interface Props {
  data: BriefingPayload
}

export function BriefingScreen({ data }: Props) {
  return (
    <div className="mx-auto max-w-5xl px-6 py-8 space-y-6">
      <div className="space-y-1">
        <p className="text-xs text-muted-foreground tabular-nums">{data.path}</p>
        {!data.ai_used && (
          <p className="text-xs text-amber-600 dark:text-amber-400">
            AI 해석 없이 표시 중 — codex 또는 claude CLI를 설치하면 더 풍부한 서술이 표시됩니다.
          </p>
        )}
      </div>

      <SectionShell
        eyebrow="What"
        title={data.what.title}
        narrative={data.what.narrative}
        metrics={data.what.metrics}
        details={data.what.details}
        variant="hero"
      />

      <SectionShell
        eyebrow="How Built"
        title={data.how_built.title}
        narrative={data.how_built.narrative}
        metrics={data.how_built.metrics}
        details={data.how_built.details}
        deepLink={data.how_built.deep_link}
      />

      <SectionShell
        eyebrow="Current State"
        title={data.current_state.title}
        narrative={data.current_state.narrative}
        metrics={data.current_state.metrics}
        details={data.current_state.details}
        deepLink={data.current_state.deep_link}
      />

      <VibeInsightsSection data={data.vibe_insights} />

      <NextActionsSection actions={data.next_actions} />

      <MicroAnalysisArea path={data.path} />
    </div>
  )
}

import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Lightbulb } from "lucide-react"
import { AxisBreakdown } from "@/components/briefing/AxisBreakdown"
import { BlindSpotBlock } from "@/components/briefing/BlindSpotBlock"
import { ProcessProxiesPanel } from "@/components/briefing/ProcessProxiesPanel"
import { EvaluationPhilosophyToggle } from "@/components/briefing/EvaluationPhilosophyToggle"
import type { VibeAxis, VibeAxisState, VibeInsights } from "@/lib/api"
import { cn } from "@/lib/utils"

const TIMELINE_TYPE_LABEL: Record<string, string> = {
  code: "코드",
  spec: "명세",
  agent: "에이전트 지침",
  validation: "검증",
  retro: "회고",
}

const TIMELINE_TYPE_COLOR: Record<string, string> = {
  code: "bg-slate-500",
  spec: "bg-blue-500",
  agent: "bg-purple-500",
  validation: "bg-emerald-500",
  retro: "bg-amber-500",
}

const STATE_LABEL: Record<VibeAxisState, string> = {
  strong: "강함",
  moderate: "보통",
  weak: "약함",
  unknown: "판단유보",
}

const STATE_RANK: Record<VibeAxisState, number> = {
  unknown: 0,
  weak: 1,
  moderate: 2,
  strong: 3,
}

const STATE_STYLES: Record<VibeAxisState, { dot: string; text: string; ring: string }> = {
  strong: {
    dot: "bg-emerald-500",
    text: "text-emerald-700 dark:text-emerald-400",
    ring: "ring-emerald-500/30",
  },
  moderate: {
    dot: "bg-amber-500",
    text: "text-amber-700 dark:text-amber-400",
    ring: "ring-amber-500/30",
  },
  weak: {
    dot: "bg-rose-500",
    text: "text-rose-700 dark:text-rose-400",
    ring: "ring-rose-500/30",
  },
  unknown: {
    dot: "bg-slate-400",
    text: "text-slate-600 dark:text-slate-400",
    ring: "ring-slate-400/30",
  },
}

interface Props {
  data: VibeInsights
}

export function VibeInsightsSection({ data }: Props) {
  return (
    <Card className="border-2 border-amber-500/30 bg-gradient-to-br from-card to-amber-500/5">
      <CardContent className="space-y-6 px-8 py-2">
        <div className="text-xs font-bold uppercase tracking-wider text-amber-700 dark:text-amber-400">
          Vibe Coding ★
        </div>
        <h2 className="text-2xl font-bold tracking-tight">바이브코딩 인사이트</h2>
        <p className="text-sm text-muted-foreground italic">
          슬로건: <strong>"주인이 있는 프로젝트"</strong>
        </p>

        <DetectedView data={data} />

        {data.process_proxies && (
          <ProcessProxiesPanel proxies={data.process_proxies} />
        )}

        {data.blind_spots && data.blind_spots.length > 0 && (
          <BlindSpotBlock items={data.blind_spots} />
        )}

        <EvaluationPhilosophyToggle />
      </CardContent>
    </Card>
  )
}

function DetectedView({ data }: { data: VibeInsights }) {
  const axes = data.axes ?? []
  const weakest = axes.reduce<VibeAxis | null>((acc, axis) => {
    if (!acc || STATE_RANK[axis.state] < STATE_RANK[acc.state]) return axis
    return acc
  }, null)

  return (
    <div className="space-y-6">
      <p className="text-sm text-muted-foreground">
        AI 협업 흔적이 감지되었습니다. 의도 / 검증 / 이어받기 세 축으로 평가합니다.
      </p>

      <div className="grid gap-3 md:grid-cols-3">
        {axes.map((axis) => (
          <AxisCard key={axis.name} axis={axis} isWeakest={axis === weakest} />
        ))}
      </div>

      {data.ai_narrative && (
        <div className="rounded-lg border bg-muted/50 p-4">
          <div className="text-xs font-semibold uppercase tracking-wide text-muted-foreground mb-2">
            AI 종합 해석
          </div>
          <p className="text-sm leading-relaxed">{data.ai_narrative}</p>
        </div>
      )}

      {data.intent_alignment && data.intent_alignment.narrative && (
        <IntentAlignmentCard alignment={data.intent_alignment} />
      )}

      {data.timeline && data.timeline.length > 0 && (
        <Timeline entries={data.timeline} />
      )}
    </div>
  )
}

function IntentAlignmentCard({
  alignment,
}: {
  alignment: NonNullable<VibeInsights["intent_alignment"]>
}) {
  return (
    <div className="rounded-lg border-2 border-blue-500/30 bg-blue-500/5 p-4">
      <div className="flex items-start gap-3">
        <Lightbulb className="h-5 w-5 text-blue-600 dark:text-blue-400 shrink-0 mt-0.5" />
        <div className="space-y-2 flex-1">
          <div className="flex items-center gap-2">
            <span className="text-xs font-bold uppercase tracking-wider text-blue-700 dark:text-blue-400">
              의도 정렬
            </span>
            <Badge variant="outline" className="text-[10px]">
              {alignment.intent_present ? "intent.md 기반" : "README 기반"}
            </Badge>
          </div>
          <p className="text-sm leading-relaxed">{alignment.narrative}</p>
        </div>
      </div>
    </div>
  )
}

function AxisCard({ axis, isWeakest }: { axis: VibeAxis; isWeakest: boolean }) {
  const styles = STATE_STYLES[axis.state]
  return (
    <div
      className={cn(
        "rounded-lg border p-4 space-y-3",
        isWeakest && axis.state !== "strong" && "border-rose-500/40 bg-rose-500/5",
      )}
    >
      <div className="flex items-center justify-between">
        <div className="text-sm font-semibold">{axis.label}</div>
        {isWeakest && axis.state !== "strong" && (
          <Badge variant="destructive" className="text-[10px]">
            약점
          </Badge>
        )}
      </div>
      <div className="flex items-center gap-2">
        <span className={cn("h-3 w-3 rounded-full", styles.dot)} />
        <span className={cn("text-lg font-bold", styles.text)}>
          {STATE_LABEL[axis.state]}
        </span>
      </div>
      <div className="text-xs text-muted-foreground">
        신호 {axis.signal_count}/{axis.signal_pool_size}개
      </div>
      {axis.top_signals && axis.top_signals.length > 0 && (
        <div className="space-y-1">
          <div className="text-[10px] font-semibold uppercase tracking-wide text-muted-foreground">
            대표 근거
          </div>
          <ul className="text-xs space-y-0.5">
            {axis.top_signals.slice(0, 3).map((sig, i) => (
              <li key={i} className="flex items-start gap-1.5">
                <span className="text-emerald-600 dark:text-emerald-400 mt-0.5">✓</span>
                <span className="leading-snug">{sig}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
      {axis.breakdown && axis.breakdown.length > 0 && (
        <AxisBreakdown items={axis.breakdown} />
      )}
    </div>
  )
}

function Timeline({
  entries,
}: {
  entries: { day: number; type: string; title: string; evidence?: string }[]
}) {
  return (
    <div className="rounded-lg border bg-card p-5">
      <div className="text-xs font-semibold uppercase tracking-wide text-muted-foreground mb-4">
        개발 과정 타임라인
      </div>
      <ol className="relative space-y-5 max-h-96 overflow-y-auto pr-2">
        <span
          className="absolute left-[7px] top-1.5 bottom-1.5 w-px bg-border"
          aria-hidden
        />
        {entries.map((entry, i) => (
          <li key={i} className="relative flex items-start gap-4 text-sm">
            <span
              className={cn(
                "relative z-10 mt-1 h-4 w-4 rounded-full shrink-0 ring-4 ring-card",
                TIMELINE_TYPE_COLOR[entry.type] || "bg-slate-500",
              )}
            />
            <div className="flex-1 min-w-0 space-y-1">
              <div className="flex items-baseline gap-2 flex-wrap">
                <Badge variant="outline" className="text-[10px] uppercase">
                  {TIMELINE_TYPE_LABEL[entry.type] || entry.type}
                </Badge>
              </div>
              <div className="font-medium leading-snug">{entry.title}</div>
              {entry.evidence && (
                <div className="text-xs text-muted-foreground font-mono break-all">
                  {entry.evidence}
                </div>
              )}
            </div>
          </li>
        ))}
      </ol>
    </div>
  )
}


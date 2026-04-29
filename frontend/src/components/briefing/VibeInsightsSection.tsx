import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import type { VibeInsights } from "@/lib/api"
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

        {!data.detected ? (
          <StarterGuide guide={data.starter_guide ?? []} />
        ) : (
          <DetectedView data={data} />
        )}
      </CardContent>
    </Card>
  )
}

function DetectedView({ data }: { data: VibeInsights }) {
  const axes = data.axes ?? []
  const weakest = axes.reduce<typeof axes[number] | null>((acc, axis) => {
    if (!acc || axis.score < acc.score) return axis
    return acc
  }, null)

  return (
    <div className="space-y-6">
      <p className="text-sm text-muted-foreground">
        AI 협업 흔적이 감지되었습니다. 세 축으로 평가합니다.
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

      {data.timeline && data.timeline.length > 0 && (
        <Timeline entries={data.timeline} />
      )}
    </div>
  )
}

function AxisCard({
  axis,
  isWeakest,
}: {
  axis: { name: string; score: number; label: string; weaknesses: string[] }
  isWeakest: boolean
}) {
  const scoreColor =
    axis.score >= 70 ? "text-emerald-600" : axis.score >= 40 ? "text-amber-600" : "text-rose-600"
  return (
    <div
      className={cn(
        "rounded-lg border p-4 space-y-3",
        isWeakest && "border-rose-500/40 bg-rose-500/5",
      )}
    >
      <div className="flex items-center justify-between">
        <div className="text-sm font-semibold">{axis.label}</div>
        {isWeakest && (
          <Badge variant="destructive" className="text-[10px]">
            약점
          </Badge>
        )}
      </div>
      <div>
        <div className={cn("text-3xl font-bold", scoreColor)}>{axis.score}</div>
        <div className="text-[10px] text-muted-foreground uppercase">/ 100</div>
      </div>
      <Progress value={axis.score} />
      {axis.weaknesses.length > 0 && (
        <ul className="text-xs text-muted-foreground space-y-0.5 mt-2">
          {axis.weaknesses.slice(0, 3).map((w, i) => (
            <li key={i}>• {w}</li>
          ))}
        </ul>
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
                <span className="text-xs text-muted-foreground tabular-nums">
                  Day {entry.day}
                </span>
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

function StarterGuide({ guide }: { guide: { action: string; reason: string }[] }) {
  return (
    <div className="space-y-4">
      <p className="text-sm leading-relaxed text-foreground/90">
        전통 방식으로 만들어진 레포로 보입니다. 바이브코딩을 시작한다면 이 첫 걸음들로 시작하세요.
      </p>
      <ul className="space-y-3">
        {guide.length === 0 ? (
          <li className="text-sm text-muted-foreground">시작 가이드 데이터가 없습니다.</li>
        ) : (
          guide.map((g, i) => (
            <li key={i} className="rounded-lg border p-4">
              <div className="font-semibold text-sm">{g.action}</div>
              <div className="text-sm text-muted-foreground mt-1 leading-relaxed">{g.reason}</div>
            </li>
          ))
        )}
      </ul>
    </div>
  )
}

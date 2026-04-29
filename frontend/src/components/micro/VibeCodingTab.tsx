import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { useTabData } from "@/components/micro/useTabData"
import { cn } from "@/lib/utils"

interface VibeEvidence {
  area: string
  path: string
  kind: string
  detail: string
}

interface VibeFinding {
  category: string
  text: string
  evidence_paths: string[]
}

interface VibeCodingPayload {
  schema_version: number
  confidence: string
  confidence_score: number
  process_areas: string[]
  evidence: VibeEvidence[]
  strengths: VibeFinding[]
  risks: VibeFinding[]
  actions: VibeFinding[]
}

const CONFIDENCE_LABEL: Record<string, { text: string; color: string }> = {
  high: { text: "강한 신호", color: "text-emerald-600 dark:text-emerald-400" },
  medium: { text: "중간 신호", color: "text-amber-600 dark:text-amber-400" },
  low: { text: "약한 신호", color: "text-rose-600 dark:text-rose-400" },
}

interface Props {
  path: string
}

export function VibeCodingTab({ path }: Props) {
  const state = useTabData<VibeCodingPayload>("vibe-coding", path)

  if (state.kind === "loading") {
    return <div className="text-sm text-muted-foreground py-8 text-center">분석 중...</div>
  }
  if (state.kind === "error") {
    return (
      <div className="text-sm text-rose-600 dark:text-rose-400 py-8 text-center">
        {state.message}
      </div>
    )
  }

  const data = state.data
  const conf = CONFIDENCE_LABEL[data.confidence] || { text: data.confidence, color: "text-muted-foreground" }

  const evidenceByArea = data.evidence.reduce<Record<string, VibeEvidence[]>>((acc, e) => {
    if (!acc[e.area]) acc[e.area] = []
    acc[e.area].push(e)
    return acc
  }, {})

  return (
    <div className="space-y-6">
      <Card>
        <CardContent>
          <div className="flex items-baseline gap-3">
            <div className="text-xs uppercase tracking-wide text-muted-foreground">
              감지 신뢰도
            </div>
            <div className={cn("text-3xl font-bold", conf.color)}>{conf.text}</div>
            <div className="text-2xl text-muted-foreground tabular-nums">
              {data.confidence_score}
            </div>
          </div>
          {data.process_areas.length > 0 && (
            <div className="mt-4 flex flex-wrap gap-2">
              {data.process_areas.map((area) => (
                <Badge key={area} variant="secondary">
                  {area}
                </Badge>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      <FindingsBlock title="잘하고 있는 것" findings={data.strengths} accent="emerald" />
      <FindingsBlock title="위험" findings={data.risks} accent="rose" />
      <FindingsBlock title="다음 행동" findings={data.actions} accent="primary" />

      {Object.keys(evidenceByArea).length > 0 && (
        <Card>
          <CardContent>
            <div className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-4">
              근거 파일 (영역별)
            </div>
            <div className="space-y-4">
              {Object.entries(evidenceByArea).map(([area, items]) => (
                <div key={area}>
                  <div className="flex items-center gap-2 mb-2">
                    <Badge variant="outline" className="text-[10px] uppercase">
                      {area}
                    </Badge>
                    <span className="text-xs text-muted-foreground tabular-nums">
                      {items.length}개
                    </span>
                  </div>
                  <ul className="space-y-1">
                    {items.map((e, i) => (
                      <li key={i} className="text-xs font-mono text-muted-foreground border-l-2 pl-3">
                        <span>{e.path}</span>
                        {e.detail && (
                          <span className="text-muted-foreground/70 ml-2">— {e.detail}</span>
                        )}
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

function FindingsBlock({
  title,
  findings,
  accent,
}: {
  title: string
  findings: VibeFinding[]
  accent: "emerald" | "rose" | "primary"
}) {
  if (findings.length === 0) return null
  const accentClass =
    accent === "emerald"
      ? "border-l-emerald-500"
      : accent === "rose"
        ? "border-l-rose-500"
        : "border-l-primary"
  return (
    <Card>
      <CardContent>
        <div className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-3">
          {title}
        </div>
        <ul className="space-y-3">
          {findings.map((f, i) => (
            <li key={i} className={cn("border-l-4 pl-4 py-1", accentClass)}>
              <div className="text-sm">{f.text}</div>
              {f.evidence_paths.length > 0 && (
                <div className="text-xs text-muted-foreground font-mono mt-1 space-y-0.5">
                  {f.evidence_paths.slice(0, 3).map((p, j) => (
                    <div key={j}>{p}</div>
                  ))}
                </div>
              )}
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  )
}

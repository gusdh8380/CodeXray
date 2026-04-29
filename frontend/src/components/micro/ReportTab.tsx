import { useState } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { useTabData } from "@/components/micro/useTabData"
import { cn } from "@/lib/utils"

interface SummaryItem {
  category?: string
  text: string
  evidence?: Record<string, unknown>
}

interface SummaryPayload {
  schema_version: number
  strengths: SummaryItem[]
  weaknesses: SummaryItem[]
  actions: SummaryItem[]
}

interface Recommendation {
  priority: number
  text: string
}

interface ReportPayload {
  schema_version: number
  path: string
  generated_date: string
  summary: SummaryPayload
  recommendations: Recommendation[]
  markdown: string
}

interface Props {
  path: string
}

export function ReportTab({ path }: Props) {
  const state = useTabData<ReportPayload>("report", path)
  const [showRaw, setShowRaw] = useState(false)

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

  const { summary, recommendations, generated_date, markdown } = state.data

  return (
    <div className="space-y-6">
      <div className="flex items-baseline justify-between">
        <div className="text-xs text-muted-foreground">
          생성: <span className="tabular-nums">{generated_date}</span>
        </div>
        <Button variant="ghost" size="sm" onClick={() => setShowRaw((v) => !v)}>
          {showRaw ? "보기 좋게" : "원본 markdown"}
        </Button>
      </div>

      {showRaw ? (
        <Card>
          <CardContent>
            <pre className="text-xs font-mono whitespace-pre-wrap break-words">
              {markdown}
            </pre>
          </CardContent>
        </Card>
      ) : (
        <>
          <div className="grid gap-3 md:grid-cols-3">
            <SummaryColumn title="잘하고 있는 것" items={summary.strengths} accent="emerald" />
            <SummaryColumn title="약점" items={summary.weaknesses} accent="rose" />
            <SummaryColumn title="다음 행동" items={summary.actions} accent="primary" />
          </div>
          {recommendations.length > 0 && (
            <Card>
              <CardContent>
                <div className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-3">
                  추천 행동 (우선순위순)
                </div>
                <ol className="space-y-2">
                  {recommendations.map((r, i) => (
                    <li key={i} className="flex items-start gap-3 text-sm">
                      <div className="flex h-6 min-w-6 items-center justify-center rounded-full bg-primary text-primary-foreground text-xs font-bold tabular-nums">
                        {r.priority}
                      </div>
                      <span className="leading-relaxed">{r.text}</span>
                    </li>
                  ))}
                </ol>
              </CardContent>
            </Card>
          )}
        </>
      )}
    </div>
  )
}

function SummaryColumn({
  title,
  items,
  accent,
}: {
  title: string
  items: SummaryItem[]
  accent: "emerald" | "rose" | "primary"
}) {
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
        {items.length === 0 ? (
          <p className="text-sm text-muted-foreground">특이사항 없음</p>
        ) : (
          <ul className="space-y-2.5">
            {items.slice(0, 5).map((item, i) => (
              <li key={i} className={cn("border-l-4 pl-3 py-0.5", accentClass)}>
                <div className="text-sm leading-relaxed">{item.text}</div>
                {item.evidence && Object.keys(item.evidence).length > 0 && (
                  <div className="text-[11px] font-mono text-muted-foreground mt-0.5">
                    {Object.entries(item.evidence)
                      .slice(0, 2)
                      .map(([k, v]) => `${k}=${String(v)}`)
                      .join(" · ")}
                  </div>
                )}
              </li>
            ))}
          </ul>
        )}
      </CardContent>
    </Card>
  )
}

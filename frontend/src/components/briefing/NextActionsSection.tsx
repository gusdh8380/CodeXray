import { Card, CardContent } from "@/components/ui/card"
import { ArrowRight } from "lucide-react"
import type { NextAction } from "@/lib/api"

interface Props {
  actions: NextAction[]
}

export function NextActionsSection({ actions }: Props) {
  return (
    <Card className="border-2 border-emerald-500/20">
      <CardContent className="space-y-6 px-8 py-2">
        <div className="text-xs font-bold uppercase tracking-wider text-emerald-700 dark:text-emerald-400">
          Next Actions
        </div>
        <h2 className="text-2xl font-bold tracking-tight">지금 뭘 해야 해</h2>
        {actions.length === 0 ? (
          <p className="text-sm text-muted-foreground">추천 행동이 없습니다.</p>
        ) : (
          <ol className="space-y-4">
            {actions.map((a, i) => (
              <li
                key={i}
                className="rounded-lg border bg-muted/30 p-4 space-y-2"
              >
                <div className="flex items-start gap-3">
                  <div className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-emerald-500 text-white text-xs font-bold">
                    {i + 1}
                  </div>
                  <div className="font-semibold text-base flex-1">{a.action}</div>
                </div>
                <div className="pl-9 space-y-1.5">
                  <div className="flex items-start gap-2 text-sm text-muted-foreground leading-relaxed">
                    <ArrowRight className="h-4 w-4 mt-0.5 shrink-0" />
                    <span>
                      <span className="font-medium text-foreground">왜? </span>
                      {a.reason}
                    </span>
                  </div>
                  <div className="text-xs text-muted-foreground pl-6">
                    <span className="font-medium">증거: </span>
                    {a.evidence}
                  </div>
                </div>
              </li>
            ))}
          </ol>
        )}
      </CardContent>
    </Card>
  )
}

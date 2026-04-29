import { useState } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { ArrowRight, Check, Copy, Sparkles } from "lucide-react"
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
              <ActionCard key={i} action={a} index={i} />
            ))}
          </ol>
        )}
      </CardContent>
    </Card>
  )
}

function ActionCard({ action, index }: { action: NextAction; index: number }) {
  const [copied, setCopied] = useState(false)

  async function copyPrompt() {
    if (!action.ai_prompt) return
    try {
      await navigator.clipboard.writeText(action.ai_prompt)
      setCopied(true)
      window.setTimeout(() => setCopied(false), 1500)
    } catch {
      /* noop */
    }
  }

  return (
    <li className="rounded-lg border bg-muted/30 p-4 space-y-2.5">
      <div className="flex items-start gap-3">
        <div className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-emerald-500 text-white text-xs font-bold">
          {index + 1}
        </div>
        <div className="font-semibold text-base flex-1">{action.action}</div>
      </div>
      <div className="pl-9 space-y-1.5">
        <div className="flex items-start gap-2 text-sm text-muted-foreground leading-relaxed">
          <ArrowRight className="h-4 w-4 mt-0.5 shrink-0" />
          <span>
            <span className="font-medium text-foreground">왜? </span>
            {action.reason}
          </span>
        </div>
        <div className="text-xs text-muted-foreground pl-6">
          <span className="font-medium">증거: </span>
          {action.evidence}
        </div>
      </div>
      {action.ai_prompt && (
        <div className="pl-9 mt-3">
          <div className="rounded-md border bg-card p-3 space-y-2">
            <div className="flex items-center justify-between gap-2">
              <span className="inline-flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wider text-blue-700 dark:text-blue-400">
                <Sparkles className="h-3 w-3" />
                Claude / Codex 에 복사
              </span>
              <Button
                size="sm"
                variant={copied ? "default" : "outline"}
                onClick={copyPrompt}
                className="h-7 text-xs"
              >
                {copied ? (
                  <>
                    <Check className="h-3 w-3 mr-1" />
                    복사됨
                  </>
                ) : (
                  <>
                    <Copy className="h-3 w-3 mr-1" />
                    복사
                  </>
                )}
              </Button>
            </div>
            <p className="text-xs leading-relaxed font-mono text-muted-foreground whitespace-pre-wrap">
              {action.ai_prompt}
            </p>
          </div>
        </div>
      )}
    </li>
  )
}

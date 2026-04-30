import { useState } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import {
  AlertTriangle,
  ArrowRight,
  Boxes,
  Check,
  CheckCircle2,
  Code2,
  Copy,
  HelpCircle,
  Sparkles,
  Sprout,
} from "lucide-react"
import type { NextAction, NextActionCategory, ZeroActionState } from "@/lib/api"

interface Props {
  actions: NextAction[]
  zeroActionState?: ZeroActionState | null
}

const CATEGORY_ORDER: NextActionCategory[] = ["code", "structural", "vibe_coding"]

const CATEGORY_META: Record<
  NextActionCategory,
  { label: string; description: string; icon: typeof Code2 }
> = {
  code: {
    label: "코드 측면",
    description: "함수·모듈 내부 변경, 테스트 보강, 에러 처리",
    icon: Code2,
  },
  structural: {
    label: "구조 측면",
    description: "모듈 분리, 의존성 정리, 아키텍처 개선",
    icon: Boxes,
  },
  vibe_coding: {
    label: "바이브코딩 측면",
    description: "AI 협업 환경·프로세스·이어받기 보강",
    icon: Sprout,
  },
}

export function NextActionsSection({ actions, zeroActionState }: Props) {
  const grouped = groupByCategory(actions)
  const hasAny = actions.length > 0

  return (
    <Card className="border-2 border-emerald-500/20">
      <CardContent className="space-y-6 px-8 py-2">
        <div className="text-xs font-bold uppercase tracking-wider text-emerald-700 dark:text-emerald-400">
          Next Actions
        </div>
        <h2 className="text-2xl font-bold tracking-tight">지금 뭘 해야 해</h2>

        <ReviewWarningBanner />

        {!hasAny ? (
          <ZeroActionView state={zeroActionState ?? null} />
        ) : (
          <div className="space-y-6">
            {CATEGORY_ORDER.map((cat) => {
              const items = grouped[cat]
              if (!items || items.length === 0) return null
              return <CategoryGroup key={cat} category={cat} items={items} />
            })}
          </div>
        )}
      </CardContent>
    </Card>
  )
}

function ZeroActionView({ state }: { state: ZeroActionState | null }) {
  if (!state || state.kind === "silent") {
    return (
      <p className="text-sm text-muted-foreground">
        고확신 추천이 없습니다. 추가 정보가 필요할 수 있어요.
      </p>
    )
  }
  if (state.kind === "praise") {
    return (
      <div className="rounded-lg border border-emerald-500/30 bg-emerald-500/5 p-4">
        <div className="flex items-start gap-2.5">
          <CheckCircle2 className="h-5 w-5 text-emerald-600 dark:text-emerald-400 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <div className="text-sm font-semibold text-emerald-700 dark:text-emerald-300">
              잘 갖춰져 있습니다
            </div>
            <p className="text-sm leading-relaxed">{state.message}</p>
          </div>
        </div>
      </div>
    )
  }
  // judgment_pending
  return (
    <div className="rounded-lg border border-slate-500/30 bg-slate-500/5 p-4">
      <div className="flex items-start gap-2.5">
        <HelpCircle className="h-5 w-5 text-slate-600 dark:text-slate-400 shrink-0 mt-0.5" />
        <div className="space-y-1">
          <div className="text-sm font-semibold text-slate-700 dark:text-slate-300">
            판단 보류
          </div>
          <p className="text-sm leading-relaxed">{state.message}</p>
        </div>
      </div>
    </div>
  )
}

function ReviewWarningBanner() {
  return (
    <div className="rounded-md border border-amber-500/40 bg-amber-500/10 p-3">
      <div className="flex items-start gap-2.5 text-sm text-amber-900 dark:text-amber-200">
        <AlertTriangle className="h-4 w-4 mt-0.5 shrink-0" />
        <p className="leading-relaxed">
          <span className="font-semibold">검토 후 진행하세요. </span>
          AI가 자동 생성한 추천입니다. 어떤 파일은 원래 자주 바뀌고 의존이 많이
          몰리는 게 자연스러운 자리(예: 시작 지점·외부 API 진입점)일 수 있어요.
          추천을 그대로 받기 전에 "이게 정말 내 프로젝트에 맞는 일인가" 한 번
          멈춰서 판단해 주세요.
        </p>
      </div>
    </div>
  )
}

function CategoryGroup({
  category,
  items,
}: {
  category: NextActionCategory
  items: NextAction[]
}) {
  const meta = CATEGORY_META[category]
  const Icon = meta.icon
  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2">
        <Icon className="h-4 w-4 text-emerald-700 dark:text-emerald-400" />
        <h3 className="text-sm font-bold tracking-tight">{meta.label}</h3>
        <span className="text-xs text-muted-foreground">{meta.description}</span>
      </div>
      <ol className="space-y-3">
        {items.map((a, i) => (
          <ActionCard key={`${category}-${i}`} action={a} index={i} />
        ))}
      </ol>
    </div>
  )
}

function groupByCategory(actions: NextAction[]): Record<NextActionCategory, NextAction[]> {
  const grouped: Record<NextActionCategory, NextAction[]> = {
    code: [],
    structural: [],
    vibe_coding: [],
  }
  for (const a of actions) {
    const cat: NextActionCategory =
      a.category === "structural" || a.category === "vibe_coding" ? a.category : "code"
    grouped[cat].push(a)
  }
  return grouped
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

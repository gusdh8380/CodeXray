import { Check, X } from "lucide-react"
import { cn } from "@/lib/utils"
import type { VibeSignal } from "@/lib/api"

interface Props {
  items: VibeSignal[]
}

export function AxisBreakdown({ items }: Props) {
  if (!items || items.length === 0) return null
  return (
    <ul className="space-y-1.5 mt-3">
      {items.map((item, i) => (
        <li
          key={i}
          className="flex items-start gap-2 text-xs"
          title={item.evidence}
        >
          <span
            className={cn(
              "mt-0.5 inline-flex h-4 w-4 items-center justify-center rounded-full shrink-0",
              item.present
                ? "bg-emerald-500/20 text-emerald-700 dark:text-emerald-400"
                : "bg-rose-500/15 text-rose-700 dark:text-rose-400",
            )}
          >
            {item.present ? <Check className="h-3 w-3" /> : <X className="h-3 w-3" />}
          </span>
          <span className="flex-1 leading-snug">
            <span className={cn(!item.present && "text-muted-foreground")}>
              {item.label}
            </span>
            {item.evidence && (
              <span className="block text-[10px] text-muted-foreground italic mt-0.5">
                {item.evidence}
              </span>
            )}
          </span>
        </li>
      ))}
    </ul>
  )
}

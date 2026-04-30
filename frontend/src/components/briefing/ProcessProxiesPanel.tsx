import { useState } from "react"
import { ChevronDown, ChevronRight, Info } from "lucide-react"
import type { ProcessProxies } from "@/lib/api"

interface Props {
  proxies: ProcessProxies
}

export function ProcessProxiesPanel({ proxies }: Props) {
  const [open, setOpen] = useState(false)
  if (!proxies || !proxies.available || proxies.items.length === 0) return null
  return (
    <div className="rounded-md border border-muted bg-muted/30 p-3 text-xs">
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        className="flex w-full items-center gap-2 text-left text-muted-foreground hover:text-foreground"
      >
        {open ? (
          <ChevronDown className="h-3.5 w-3.5" />
        ) : (
          <ChevronRight className="h-3.5 w-3.5" />
        )}
        <Info className="h-3.5 w-3.5" />
        <span className="font-medium">참고용 — {proxies.note}</span>
      </button>
      {open && (
        <ul className="mt-3 space-y-1 pl-6">
          {proxies.items.map((item, i) => (
            <li key={i} className="flex items-baseline justify-between gap-3">
              <span>{item.label}</span>
              <span className="font-mono tabular-nums">{item.value}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}

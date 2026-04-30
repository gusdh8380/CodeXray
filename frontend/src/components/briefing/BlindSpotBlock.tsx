import { Eye } from "lucide-react"

interface Props {
  items: string[]
}

export function BlindSpotBlock({ items }: Props) {
  if (!items || items.length === 0) return null
  return (
    <div className="rounded-lg border border-slate-500/30 bg-slate-500/5 p-4 space-y-3">
      <div className="flex items-center gap-2">
        <Eye className="h-4 w-4 text-slate-600 dark:text-slate-400" />
        <h3 className="text-sm font-bold tracking-tight">이 도구가 못 보는 것</h3>
      </div>
      <p className="text-xs text-muted-foreground leading-relaxed">
        다음 항목들은 코드만 봐서는 판단할 수 없습니다. 화면 상태와 무관하게
        직접 자가 점검해 주세요.
      </p>
      <ul className="space-y-1.5 text-xs leading-relaxed">
        {items.map((item, i) => (
          <li key={i} className="flex items-start gap-2">
            <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-slate-400" />
            <span>{item}</span>
          </li>
        ))}
      </ul>
    </div>
  )
}

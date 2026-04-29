import type { ArchModule } from "@/lib/architecture"

interface Props {
  modules: ArchModule[]
}

export function ModuleLegend({ modules }: Props) {
  return (
    <div className="flex flex-wrap gap-2 text-xs">
      {modules.slice(0, 12).map((m) => (
        <div
          key={m.name}
          className="inline-flex items-center gap-1.5 rounded-md border px-2 py-1"
          style={{ borderColor: m.color }}
        >
          <span
            className="h-2 w-2 rounded-full"
            style={{ background: m.color }}
            aria-hidden
          />
          <span className="font-mono">{m.name}</span>
          <span className="text-muted-foreground tabular-nums">{m.node_count}</span>
        </div>
      ))}
      {modules.length > 12 && (
        <span className="text-muted-foreground self-center">+{modules.length - 12}개</span>
      )}
    </div>
  )
}

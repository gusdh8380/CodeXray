import { useState } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { useTabData } from "@/components/micro/useTabData"
import { ForceView } from "@/components/micro/architecture/ForceView"
import { LayeredView } from "@/components/micro/architecture/LayeredView"
import { ModuleLegend } from "@/components/micro/architecture/ModuleLegend"
import type { ArchitectureView } from "@/lib/architecture"
import { cn } from "@/lib/utils"

interface ViewSpec {
  id: "force" | "layered" | "hull" | "bundling"
  label: string
  desc: string
  disabled?: boolean
}

const VIEWS: ViewSpec[] = [
  { id: "force", label: "힘 기반", desc: "연결 관계가 잘 보임" },
  { id: "layered", label: "레이어드", desc: "흐름 방향이 잘 보임" },
  { id: "hull", label: "모듈 헐", desc: "준비 중", disabled: true },
  { id: "bundling", label: "방사형 번들", desc: "준비 중", disabled: true },
]

type ViewId = ViewSpec["id"]

interface Props {
  path: string
}

export function GraphTab({ path }: Props) {
  const state = useTabData<ArchitectureView>("architecture", path)
  const [view, setView] = useState<ViewId>("force")

  if (state.kind === "loading") {
    return (
      <div className="text-sm text-muted-foreground py-12 text-center">
        의존성 그래프를 만드는 중...
      </div>
    )
  }
  if (state.kind === "error") {
    return (
      <div className="text-sm text-rose-600 dark:text-rose-400 py-8 text-center">
        {state.message}
      </div>
    )
  }

  const { stats, modules } = state.data

  return (
    <div className="space-y-4">
      <Card>
        <CardContent className="space-y-3">
          <div className="flex flex-wrap items-center gap-2">
            {VIEWS.map((v) => (
              <button
                key={v.id}
                type="button"
                disabled={v.disabled}
                onClick={() => !v.disabled && setView(v.id)}
                className={cn(
                  "rounded-md border px-3 py-1.5 text-sm transition-colors",
                  view === v.id
                    ? "border-primary bg-primary text-primary-foreground"
                    : "border-input hover:bg-accent hover:text-accent-foreground",
                  v.disabled && "opacity-40 cursor-not-allowed",
                )}
                title={v.desc}
              >
                {v.label}
              </button>
            ))}
            <div className="ml-auto text-xs text-muted-foreground tabular-nums">
              {stats.node_count} 노드 · {stats.edge_count} 엣지 · {stats.module_count} 모듈
              {stats.is_dag ? " · DAG" : ` · 순환 ${stats.largest_scc}`}
            </div>
          </div>
          <ModuleLegend modules={modules} />
        </CardContent>
      </Card>

      {view === "force" && <ForceView data={state.data} height={680} />}
      {view === "layered" && <LayeredView data={state.data} height={760} />}
    </div>
  )
}

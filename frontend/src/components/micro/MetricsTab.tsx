import { useState } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { useTabData } from "@/components/micro/useTabData"
import { cn } from "@/lib/utils"

interface MetricsNode {
  path: string
  language: string
  fan_in: number
  fan_out: number
  external_fan_out: number
}

interface MetricsPayload {
  schema_version: number
  graph: {
    is_dag: boolean
    largest_scc_size: number
    cycle_count: number
  }
  nodes: MetricsNode[]
}

function couplingRisk(coupling: number): { label: string; color: string } {
  if (coupling >= 30) return { label: "매우 높음", color: "text-rose-600 dark:text-rose-400" }
  if (coupling >= 15) return { label: "높음", color: "text-orange-600 dark:text-orange-400" }
  if (coupling >= 7) return { label: "보통", color: "text-amber-600 dark:text-amber-400" }
  return { label: "낮음", color: "text-emerald-600 dark:text-emerald-400" }
}

interface Props {
  path: string
}

export function MetricsTab({ path }: Props) {
  const state = useTabData<MetricsPayload>("metrics", path)
  const [filter, setFilter] = useState("")

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

  const sorted = [...state.data.nodes]
    .map((n) => ({ ...n, coupling: n.fan_in + n.fan_out + n.external_fan_out }))
    .sort((a, b) => b.coupling - a.coupling)
  const filtered = filter
    ? sorted.filter((n) => n.path.toLowerCase().includes(filter.toLowerCase()))
    : sorted
  const top = filtered.slice(0, 50)

  return (
    <div className="space-y-6">
      <div className="grid gap-3 grid-cols-2 md:grid-cols-3">
        <Card>
          <CardContent>
            <div className="text-xs text-muted-foreground uppercase tracking-wide">DAG?</div>
            <div className="text-2xl font-bold mt-1">
              {state.data.graph.is_dag ? "✓ 순환 없음" : "✗ 순환 존재"}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent>
            <div className="text-xs text-muted-foreground uppercase tracking-wide">최대 순환 묶음</div>
            <div className="text-2xl font-bold mt-1 tabular-nums">
              {state.data.graph.largest_scc_size} files
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent>
            <div className="text-xs text-muted-foreground uppercase tracking-wide">총 노드</div>
            <div className="text-2xl font-bold mt-1 tabular-nums">{state.data.nodes.length}</div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardContent>
          <div className="flex items-center justify-between mb-4 gap-4">
            <div className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              결합도 상위 50
            </div>
            <Input
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              placeholder="파일 경로 필터..."
              className="max-w-xs"
            />
          </div>
          <table className="w-full text-sm">
            <thead className="text-xs text-muted-foreground uppercase">
              <tr>
                <th className="text-left font-medium py-1.5">파일</th>
                <th className="text-right font-medium py-1.5" title="이 파일에 의존하는 파일 수">
                  fan-in
                </th>
                <th className="text-right font-medium py-1.5" title="이 파일이 의존하는 파일 수">
                  fan-out
                </th>
                <th className="text-right font-medium py-1.5">외부</th>
                <th className="text-right font-medium py-1.5">결합도</th>
                <th className="text-right font-medium py-1.5">위험도</th>
              </tr>
            </thead>
            <tbody>
              {top.map((n) => {
                const risk = couplingRisk(n.coupling)
                return (
                  <tr key={n.path} className="border-t">
                    <td className="py-2 font-mono text-xs truncate max-w-[340px]">{n.path}</td>
                    <td className="py-2 text-right tabular-nums">{n.fan_in}</td>
                    <td className="py-2 text-right tabular-nums">{n.fan_out}</td>
                    <td className="py-2 text-right tabular-nums text-muted-foreground">
                      {n.external_fan_out}
                    </td>
                    <td className="py-2 text-right tabular-nums font-semibold">{n.coupling}</td>
                    <td className={cn("py-2 text-right text-xs font-semibold", risk.color)}>
                      {risk.label}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
          {filtered.length > 50 && (
            <div className="text-xs text-muted-foreground text-center mt-3">
              {filtered.length - 50}개 더 있음 (필터 조건을 좁혀주세요)
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

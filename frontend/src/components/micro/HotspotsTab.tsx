import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { useTabData } from "@/components/micro/useTabData"
import { cn } from "@/lib/utils"

interface HotspotFile {
  path: string
  category: string
  change_count: number
  coupling: number
}

interface HotspotsPayload {
  schema_version: number
  summary: Record<string, number>
  files: HotspotFile[]
}

const CATEGORY_LABEL: Record<string, string> = {
  hotspot: "Hotspot (자주 변경 + 높은 결합)",
  active_stable: "활발 안정",
  neglected_complex: "방치 복잡",
  stable: "안정",
}

const CATEGORY_COLOR: Record<string, string> = {
  hotspot: "bg-rose-500",
  active_stable: "bg-amber-500",
  neglected_complex: "bg-yellow-500",
  stable: "bg-slate-400",
}

interface Props {
  path: string
}

export function HotspotsTab({ path }: Props) {
  const state = useTabData<HotspotsPayload>("hotspots", path)

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

  const { summary, files } = state.data
  const ranked = [...files]
    .sort((a, b) => b.change_count * b.coupling - a.change_count * a.coupling)
    .slice(0, 30)

  return (
    <div className="space-y-6">
      <div className="grid gap-3 grid-cols-2 md:grid-cols-4">
        {Object.entries(summary).map(([key, count]) => (
          <Card key={key}>
            <CardContent>
              <div className="flex items-center gap-2">
                <span
                  className={cn("h-2.5 w-2.5 rounded-full", CATEGORY_COLOR[key] || "bg-slate-400")}
                />
                <div className="text-xs text-muted-foreground uppercase tracking-wide truncate">
                  {CATEGORY_LABEL[key] || key}
                </div>
              </div>
              <div className="text-3xl font-bold tabular-nums mt-2">{count}</div>
            </CardContent>
          </Card>
        ))}
      </div>

      <Card>
        <CardContent>
          <div className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-3">
            우선순위 상위 30개 파일
          </div>
          <table className="w-full text-sm">
            <thead className="text-xs text-muted-foreground uppercase">
              <tr>
                <th className="text-left font-medium py-1.5">파일</th>
                <th className="text-left font-medium py-1.5">분류</th>
                <th className="text-right font-medium py-1.5">변경</th>
                <th className="text-right font-medium py-1.5">결합도</th>
                <th className="text-right font-medium py-1.5">우선순위</th>
              </tr>
            </thead>
            <tbody>
              {ranked.map((f) => (
                <tr key={f.path} className="border-t">
                  <td className="py-2 font-mono text-xs truncate max-w-[360px]">{f.path}</td>
                  <td className="py-2">
                    <Badge variant="outline" className="text-[10px]">
                      <span
                        className={cn(
                          "mr-1.5 h-1.5 w-1.5 rounded-full inline-block",
                          CATEGORY_COLOR[f.category] || "bg-slate-400",
                        )}
                      />
                      {CATEGORY_LABEL[f.category] || f.category}
                    </Badge>
                  </td>
                  <td className="py-2 text-right tabular-nums">{f.change_count}</td>
                  <td className="py-2 text-right tabular-nums">{f.coupling}</td>
                  <td className="py-2 text-right tabular-nums font-semibold">
                    {f.change_count * f.coupling}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </CardContent>
      </Card>
    </div>
  )
}

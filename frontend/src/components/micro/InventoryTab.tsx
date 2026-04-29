import { Card, CardContent } from "@/components/ui/card"
import { useTabData } from "@/components/micro/useTabData"

interface InventoryRow {
  language: string
  file_count: number
  loc: number
  newest_change: string | null
  oldest_change: string | null
}

interface InventoryPayload {
  schema_version: number
  rows: InventoryRow[]
}

interface Props {
  path: string
}

export function InventoryTab({ path }: Props) {
  const state = useTabData<InventoryPayload>("inventory", path)

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

  const rows = [...state.data.rows].sort((a, b) => b.loc - a.loc)
  const totalLoc = rows.reduce((s, r) => s + r.loc, 0)
  const totalFiles = rows.reduce((s, r) => s + r.file_count, 0)

  return (
    <Card>
      <CardContent>
        <div className="flex items-baseline gap-6 mb-6">
          <div>
            <div className="text-xs text-muted-foreground uppercase tracking-wide">총 파일</div>
            <div className="text-3xl font-bold tabular-nums">{totalFiles}</div>
          </div>
          <div>
            <div className="text-xs text-muted-foreground uppercase tracking-wide">총 LoC</div>
            <div className="text-3xl font-bold tabular-nums">{totalLoc.toLocaleString()}</div>
          </div>
          <div>
            <div className="text-xs text-muted-foreground uppercase tracking-wide">언어 수</div>
            <div className="text-3xl font-bold tabular-nums">{rows.length}</div>
          </div>
        </div>
        <table className="w-full text-sm">
          <thead className="text-xs text-muted-foreground uppercase">
            <tr>
              <th className="text-left font-medium py-1.5">언어</th>
              <th className="text-right font-medium py-1.5">파일</th>
              <th className="text-right font-medium py-1.5">LoC</th>
              <th className="text-right font-medium py-1.5">비중</th>
              <th className="text-left font-medium py-1.5 pl-4">최신 변경</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => {
              const share = totalLoc > 0 ? (r.loc * 100) / totalLoc : 0
              return (
                <tr key={r.language} className="border-t">
                  <td className="py-2 font-medium">{r.language}</td>
                  <td className="py-2 text-right tabular-nums">{r.file_count}</td>
                  <td className="py-2 text-right tabular-nums">{r.loc.toLocaleString()}</td>
                  <td className="py-2 text-right tabular-nums">
                    <div className="flex items-center justify-end gap-2">
                      <div className="w-16 h-1.5 bg-secondary rounded-full overflow-hidden">
                        <div
                          className="h-full bg-primary"
                          style={{ width: `${share}%` }}
                        />
                      </div>
                      {share.toFixed(1)}%
                    </div>
                  </td>
                  <td className="py-2 text-left text-xs text-muted-foreground pl-4 tabular-nums">
                    {r.newest_change || "—"}
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </CardContent>
    </Card>
  )
}

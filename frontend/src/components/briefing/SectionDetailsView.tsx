import type { SectionDetails } from "@/lib/api"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"

interface Props {
  details: SectionDetails
}

const HOTSPOT_CATEGORY_LABEL: Record<string, string> = {
  hotspot: "Hotspot",
  active_stable: "활발 안정",
  neglected_complex: "방치 복잡",
  stable: "안정",
}

const HOTSPOT_CATEGORY_COLOR: Record<string, string> = {
  hotspot: "bg-rose-500",
  active_stable: "bg-amber-500",
  neglected_complex: "bg-yellow-500",
  stable: "bg-slate-400",
}

const GRADE_COLOR: Record<string, string> = {
  A: "text-emerald-600 dark:text-emerald-400",
  B: "text-emerald-500 dark:text-emerald-400",
  C: "text-amber-600 dark:text-amber-400",
  D: "text-orange-600 dark:text-orange-400",
  F: "text-rose-600 dark:text-rose-400",
}

export function SectionDetailsView({ details }: Props) {
  return (
    <div className="space-y-4">
      {details.languages && details.languages.length > 0 && (
        <Languages rows={details.languages} />
      )}
      {details.top_coupled && details.top_coupled.length > 0 && (
        <CoupledFiles rows={details.top_coupled} isDag={details.is_dag} />
      )}
      {details.entrypoints && details.entrypoints.length > 0 && (
        <Entrypoints rows={details.entrypoints} />
      )}
      {details.dimensions && details.dimensions.length > 0 && (
        <QualityDimensions rows={details.dimensions} />
      )}
      {details.hotspots && details.hotspots.length > 0 && (
        <Hotspots rows={details.hotspots} />
      )}
    </div>
  )
}

function Languages({ rows }: { rows: NonNullable<SectionDetails["languages"]> }) {
  const max = Math.max(...rows.map((r) => r.share))
  return (
    <DetailBlock title="언어 분포">
      <div className="space-y-2">
        {rows.map((r) => (
          <div key={r.language} className="space-y-1">
            <div className="flex items-baseline justify-between text-sm">
              <span className="font-medium">{r.language}</span>
              <span className="text-muted-foreground tabular-nums">
                {r.files} files · {r.loc.toLocaleString()} LoC · {r.share}%
              </span>
            </div>
            <div className="h-1.5 bg-secondary rounded-full overflow-hidden">
              <div
                className="h-full bg-primary"
                style={{ width: `${(r.share / max) * 100}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </DetailBlock>
  )
}

function CoupledFiles({
  rows,
  isDag,
}: {
  rows: NonNullable<SectionDetails["top_coupled"]>
  isDag?: boolean
}) {
  return (
    <DetailBlock
      title="결합도 상위 파일"
      hint={
        isDag === false
          ? "주의: 그래프에 순환 의존이 있습니다"
          : isDag
            ? "그래프는 순환 없는 DAG"
            : undefined
      }
    >
      <table className="w-full text-sm">
        <thead className="text-xs text-muted-foreground uppercase">
          <tr>
            <th className="text-left font-medium py-1">파일</th>
            <th className="text-right font-medium py-1">의존받음</th>
            <th className="text-right font-medium py-1">의존함</th>
            <th className="text-right font-medium py-1">결합도</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.path} className="border-t">
              <td className="py-1.5 font-mono text-xs truncate max-w-[280px]">
                {r.path}
              </td>
              <td className="py-1.5 text-right tabular-nums">{r.fan_in}</td>
              <td className="py-1.5 text-right tabular-nums">
                {r.fan_out + r.external_fan_out}
              </td>
              <td className="py-1.5 text-right tabular-nums font-semibold">
                {r.coupling}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </DetailBlock>
  )
}

function Entrypoints({
  rows,
}: {
  rows: NonNullable<SectionDetails["entrypoints"]>
}) {
  return (
    <DetailBlock title="진입점">
      <ul className="space-y-1.5">
        {rows.map((r, i) => (
          <li key={`${r.path}-${i}`} className="flex items-center gap-2 text-sm">
            <Badge variant="outline" className="text-[10px] uppercase">
              {r.kind}
            </Badge>
            <span className="font-mono text-xs truncate">{r.path}</span>
          </li>
        ))}
      </ul>
    </DetailBlock>
  )
}

function QualityDimensions({
  rows,
}: {
  rows: NonNullable<SectionDetails["dimensions"]>
}) {
  return (
    <DetailBlock title="품질 차원">
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
        {rows.map((r) => (
          <div key={r.name} className="flex items-center justify-between rounded border px-3 py-2">
            <span className="text-sm capitalize">{r.name}</span>
            <span
              className={cn(
                "font-mono text-sm font-bold",
                GRADE_COLOR[r.grade] || "text-muted-foreground",
              )}
            >
              {r.grade}
              {r.score !== null && (
                <span className="text-xs text-muted-foreground font-normal ml-1">
                  {r.score}
                </span>
              )}
            </span>
          </div>
        ))}
      </div>
    </DetailBlock>
  )
}

function Hotspots({ rows }: { rows: NonNullable<SectionDetails["hotspots"]> }) {
  return (
    <DetailBlock title="Hotspot 상위 파일">
      <table className="w-full text-sm">
        <thead className="text-xs text-muted-foreground uppercase">
          <tr>
            <th className="text-left font-medium py-1">파일</th>
            <th className="text-left font-medium py-1">분류</th>
            <th className="text-right font-medium py-1">변경</th>
            <th className="text-right font-medium py-1">결합</th>
            <th className="text-right font-medium py-1">우선순위</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.path} className="border-t">
              <td className="py-1.5 font-mono text-xs truncate max-w-[260px]">
                {r.path}
              </td>
              <td className="py-1.5">
                <span className="inline-flex items-center gap-1.5 text-xs">
                  <span
                    className={cn(
                      "h-2 w-2 rounded-full",
                      HOTSPOT_CATEGORY_COLOR[r.category] || "bg-slate-400",
                    )}
                  />
                  {HOTSPOT_CATEGORY_LABEL[r.category] || r.category}
                </span>
              </td>
              <td className="py-1.5 text-right tabular-nums">{r.changes}</td>
              <td className="py-1.5 text-right tabular-nums">{r.coupling}</td>
              <td className="py-1.5 text-right tabular-nums font-semibold">
                {r.priority}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </DetailBlock>
  )
}

function DetailBlock({
  title,
  hint,
  children,
}: {
  title: string
  hint?: string
  children: React.ReactNode
}) {
  return (
    <div className="rounded-lg border bg-muted/30 p-4">
      <div className="flex items-baseline justify-between mb-3">
        <div className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
          {title}
        </div>
        {hint && <div className="text-[10px] text-muted-foreground">{hint}</div>}
      </div>
      {children}
    </div>
  )
}

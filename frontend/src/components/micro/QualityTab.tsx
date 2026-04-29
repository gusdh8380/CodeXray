import { Card, CardContent } from "@/components/ui/card"
import { useTabData } from "@/components/micro/useTabData"
import { cn } from "@/lib/utils"

interface QualityDimension {
  grade: string | null
  score: number | null
  warnings?: string[]
  metrics?: Record<string, unknown>
}

interface QualityPayload {
  schema_version: number
  overall: { grade: string | null; score: number | null }
  dimensions: Record<string, QualityDimension>
}

const GRADE_COLOR: Record<string, string> = {
  A: "text-emerald-600 dark:text-emerald-400",
  B: "text-emerald-500 dark:text-emerald-400",
  C: "text-amber-600 dark:text-amber-400",
  D: "text-orange-600 dark:text-orange-400",
  F: "text-rose-600 dark:text-rose-400",
}

const GRADE_INTERPRETATION: Record<string, string> = {
  A: "매우 좋음",
  B: "좋음",
  C: "보통",
  D: "주의 필요",
  F: "위험 — 즉시 검토",
}

const DIMENSION_LABELS: Record<string, string> = {
  test: "테스트",
  documentation: "문서화",
  duplication: "중복도",
  coupling: "결합도",
  complexity: "복잡도",
  cohesion: "응집도",
}

interface Props {
  path: string
}

export function QualityTab({ path }: Props) {
  const state = useTabData<QualityPayload>("quality", path)

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

  const { overall, dimensions } = state.data
  const grade = overall.grade || "N/A"
  const score = overall.score
  const interpretation = GRADE_INTERPRETATION[grade] || ""

  return (
    <div className="space-y-6">
      <Card>
        <CardContent>
          <div className="flex items-baseline gap-4">
            <div className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
              종합
            </div>
            <div
              className={cn("text-5xl font-bold", GRADE_COLOR[grade] || "text-muted-foreground")}
            >
              {grade}
            </div>
            {score !== null && (
              <div className="text-2xl text-muted-foreground tabular-nums">{score}</div>
            )}
            {interpretation && (
              <div className="text-sm text-muted-foreground">— {interpretation}</div>
            )}
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
        {Object.entries(dimensions)
          .sort(([a], [b]) => a.localeCompare(b))
          .map(([name, dim]) => (
            <Card key={name}>
              <CardContent className="space-y-3">
                <div className="flex items-baseline justify-between">
                  <div className="text-sm font-semibold capitalize">
                    {DIMENSION_LABELS[name] || name}
                  </div>
                  <div className="flex items-baseline gap-1.5">
                    <span
                      className={cn(
                        "text-2xl font-bold",
                        GRADE_COLOR[dim.grade || ""] || "text-muted-foreground",
                      )}
                    >
                      {dim.grade || "N/A"}
                    </span>
                    {dim.score !== null && (
                      <span className="text-sm text-muted-foreground tabular-nums">
                        {dim.score}
                      </span>
                    )}
                  </div>
                </div>
                {dim.warnings && dim.warnings.length > 0 && (
                  <ul className="text-xs text-muted-foreground space-y-1">
                    {dim.warnings.slice(0, 3).map((w, i) => (
                      <li key={i}>• {w}</li>
                    ))}
                  </ul>
                )}
              </CardContent>
            </Card>
          ))}
      </div>
    </div>
  )
}

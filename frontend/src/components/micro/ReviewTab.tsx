import { useEffect, useRef, useState } from "react"
import { Loader2, X } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"

interface DimensionReview {
  score: number
  evidence_lines: number[]
  comment: string
  suggestion: string
}

interface FileReview {
  path: string
  confidence: string
  limitations: string
  dimensions: Record<string, DimensionReview>
}

interface SkippedFile {
  path: string
  reason: string
}

interface ReviewResult {
  schema_version: number
  backend: string
  files_reviewed: number
  skipped: SkippedFile[]
  reviews: FileReview[]
}

interface ReviewJobStatus {
  job_id: string
  status: "running" | "completed" | "failed" | "cancelled"
  result?: ReviewResult
  error?: string
}

type State =
  | { kind: "idle" }
  | { kind: "running"; jobId: string }
  | { kind: "done"; result: ReviewResult }
  | { kind: "failed"; message: string }
  | { kind: "cancelled" }

const DIMENSION_LABELS: Record<string, string> = {
  readability: "가독성",
  design: "설계",
  maintainability: "유지보수성",
  risk: "위험",
}

const CONFIDENCE_LABEL: Record<string, string> = {
  high: "높음",
  medium: "중간",
  low: "낮음",
}

interface Props {
  path: string
}

export function ReviewTab({ path }: Props) {
  const [state, setState] = useState<State>({ kind: "idle" })
  const pollRef = useRef<number | null>(null)

  useEffect(() => {
    return () => {
      if (pollRef.current) window.clearTimeout(pollRef.current)
    }
  }, [])

  async function run() {
    try {
      const res = await fetch("/api/review", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ path }),
      })
      if (!res.ok) {
        const body = await res.json().catch(() => ({}))
        setState({ kind: "failed", message: body?.error || `시작 실패: ${res.status}` })
        return
      }
      const { job_id } = await res.json()
      setState({ kind: "running", jobId: job_id })
      poll(job_id)
    } catch (err) {
      setState({ kind: "failed", message: (err as Error).message })
    }
  }

  function poll(jobId: string) {
    pollRef.current = window.setTimeout(async () => {
      try {
        const res = await fetch(`/api/review/status/${jobId}`)
        const body: ReviewJobStatus = await res.json()
        if (body.status === "running") {
          poll(jobId)
          return
        }
        if (body.status === "completed" && body.result) {
          setState({ kind: "done", result: body.result })
          return
        }
        if (body.status === "cancelled") {
          setState({ kind: "cancelled" })
          return
        }
        setState({ kind: "failed", message: body.error || "리뷰 실패" })
      } catch (err) {
        setState({ kind: "failed", message: (err as Error).message })
      }
    }, 2000)
  }

  async function cancel(jobId: string) {
    if (pollRef.current) window.clearTimeout(pollRef.current)
    try {
      await fetch(`/api/review/cancel/${jobId}`, { method: "POST" })
    } catch {
      /* ignore */
    }
    setState({ kind: "cancelled" })
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardContent className="space-y-3">
          <div className="text-xs font-semibold uppercase tracking-wider text-amber-600 dark:text-amber-400">
            ⚠ AI Review (명시 실행)
          </div>
          <p className="text-sm text-muted-foreground leading-relaxed">
            상위 hotspot 파일에 대해 AI가 정성 리뷰를 수행합니다. <strong className="text-foreground">1~5분</strong> 정도 걸리며 codex/claude CLI를 통해 외부로 코드가 전송됩니다.
          </p>
          {state.kind === "idle" && (
            <Button onClick={run}>리뷰 실행</Button>
          )}
          {state.kind === "running" && (
            <div className="flex items-center gap-3">
              <Loader2 className="h-4 w-4 animate-spin" />
              <span className="text-sm">리뷰 실행 중...</span>
              <Button
                variant="outline"
                size="sm"
                onClick={() => cancel(state.jobId)}
              >
                <X className="h-3 w-3 mr-1" />
                취소
              </Button>
            </div>
          )}
          {state.kind === "cancelled" && (
            <div className="flex items-center gap-3">
              <span className="text-sm text-muted-foreground">취소되었습니다.</span>
              <Button variant="outline" size="sm" onClick={run}>
                다시 실행
              </Button>
            </div>
          )}
          {state.kind === "failed" && (
            <div className="space-y-2">
              <div className="text-sm text-rose-600 dark:text-rose-400">{state.message}</div>
              <Button variant="outline" size="sm" onClick={run}>
                다시 실행
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {state.kind === "done" && <ReviewResultView result={state.result} />}
    </div>
  )
}

function ReviewResultView({ result }: { result: ReviewResult }) {
  return (
    <div className="space-y-4">
      <div className="flex items-baseline gap-3 text-sm">
        <Badge variant="secondary">{result.backend}</Badge>
        <span className="text-muted-foreground tabular-nums">
          {result.files_reviewed} 파일 리뷰됨
        </span>
        {result.skipped.length > 0 && (
          <span className="text-xs text-muted-foreground">
            ({result.skipped.length}개 스킵)
          </span>
        )}
      </div>
      {result.reviews.map((r) => (
        <FileReviewCard key={r.path} review={r} />
      ))}
      {result.reviews.length === 0 && (
        <p className="text-sm text-muted-foreground">리뷰된 파일이 없습니다.</p>
      )}
    </div>
  )
}

function FileReviewCard({ review }: { review: FileReview }) {
  return (
    <Card>
      <CardContent className="space-y-3">
        <div className="flex items-center gap-2 flex-wrap">
          <code className="font-mono text-xs">{review.path}</code>
          <Badge variant="outline" className="text-[10px]">
            신뢰도 {CONFIDENCE_LABEL[review.confidence] || review.confidence}
          </Badge>
        </div>
        {review.limitations && (
          <p className="text-xs text-muted-foreground italic">{review.limitations}</p>
        )}
        <div className="grid gap-2 md:grid-cols-2">
          {Object.entries(review.dimensions).map(([name, dim]) => (
            <div
              key={name}
              className={cn(
                "rounded-lg border p-3 space-y-1.5",
                dim.score >= 80
                  ? "border-emerald-500/40"
                  : dim.score >= 60
                    ? "border-amber-500/40"
                    : "border-rose-500/40",
              )}
            >
              <div className="flex items-baseline justify-between">
                <span className="text-xs font-semibold uppercase tracking-wide">
                  {DIMENSION_LABELS[name] || name}
                </span>
                <span className="text-lg font-bold tabular-nums">{dim.score}</span>
              </div>
              <div className="text-sm leading-relaxed">{dim.comment}</div>
              {dim.suggestion && (
                <div className="text-xs text-muted-foreground leading-relaxed border-l-2 border-primary/40 pl-2">
                  → {dim.suggestion}
                </div>
              )}
              {dim.evidence_lines.length > 0 && (
                <div className="text-[11px] text-muted-foreground font-mono">
                  L{dim.evidence_lines.join(", L")}
                </div>
              )}
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}

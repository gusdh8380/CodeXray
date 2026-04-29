import { useEffect, useRef, useState } from "react"
import { Header } from "@/components/Header"
import { BriefingProgress } from "@/components/BriefingProgress"
import { BriefingScreen } from "@/components/briefing/BriefingScreen"
import { Card, CardContent } from "@/components/ui/card"
import {
  pollBriefing,
  type BriefingPayload,
  type BriefingJobStatus,
} from "@/lib/api"
import { rememberPath } from "@/lib/recent-paths"

type AnalysisState =
  | { kind: "idle" }
  | { kind: "running"; status: BriefingJobStatus | null }
  | { kind: "done"; data: BriefingPayload }
  | { kind: "error"; message: string }

export default function App() {
  const [path, setPath] = useState<string>("")
  const [state, setState] = useState<AnalysisState>({ kind: "idle" })
  const abortRef = useRef<AbortController | null>(null)

  useEffect(() => {
    fetch("/api/default-path")
      .then((r) => (r.ok ? r.json() : null))
      .then((d) => {
        if (d?.path) setPath(d.path)
      })
      .catch(() => {})
  }, [])

  function startAnalysis(target: string) {
    abortRef.current?.abort()
    const controller = new AbortController()
    abortRef.current = controller
    rememberPath(target)
    setState({ kind: "running", status: null })
    pollBriefing(
      target,
      (status) => setState({ kind: "running", status }),
      controller.signal,
    )
      .then((data) => setState({ kind: "done", data }))
      .catch((err: Error) => {
        if (err.message === "aborted") return
        setState({ kind: "error", message: err.message })
      })
  }

  return (
    <div className="min-h-screen bg-background">
      <Header
        path={path}
        onPathChange={setPath}
        onSubmit={startAnalysis}
        isAnalyzing={state.kind === "running"}
      />
      <main>
        {state.kind === "idle" && <Welcome />}
        {state.kind === "running" && <BriefingProgress status={state.status} />}
        {state.kind === "done" && <BriefingScreen data={state.data} />}
        {state.kind === "error" && <ErrorPanel message={state.message} />}
      </main>
    </div>
  )
}

function Welcome() {
  return (
    <div className="mx-auto max-w-3xl py-24 px-6">
      <div className="text-center mb-12">
        <div className="inline-block rounded-full bg-primary/10 px-3 py-1 text-xs font-medium text-primary mb-4">
          로컬 코드베이스 분석
        </div>
        <h2 className="text-4xl font-bold tracking-tight mb-4">
          레포 경로를 입력하고 Enter
        </h2>
        <p className="text-muted-foreground leading-relaxed text-lg">
          CodeXray는 코드를 읽고{" "}
          <strong className="text-foreground">이게 뭐고, 어떤 상태고, 뭘 먼저 봐야 하는지</strong>를{" "}
          한 화면에서 설명합니다.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-3 mt-12">
        <FlowStep step="1" title="이게 뭐야" desc="AI가 원본 코드를 읽고 프로젝트 정체와 도메인을 한 문단으로 요약" />
        <FlowStep step="2" title="지금 상태" desc="품질 등급, 위험 파일, 결합도 표를 인라인으로 함께 표시" />
        <FlowStep step="3" title="다음 행동" desc="행동 / 왜 그게 필요한지 / 분석 증거 인용 — 세 필드로 명확하게" />
      </div>

      <div className="mt-12 rounded-xl border bg-amber-500/5 border-amber-500/30 p-5">
        <div className="flex items-start gap-3">
          <span className="text-2xl">★</span>
          <div>
            <div className="font-semibold mb-1">바이브코딩 인사이트</div>
            <p className="text-sm text-muted-foreground leading-relaxed">
              파일·git history에서 AI 협업 흔적을 자동 감지하고, <strong className="text-foreground">환경 구축 / 개발 과정 / 이어받기 가능성</strong> 세 축으로 평가합니다. 미감지 레포에는 시작 가이드를 보여줍니다.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

function FlowStep({ step, title, desc }: { step: string; title: string; desc: string }) {
  return (
    <div className="rounded-lg border bg-card p-5">
      <div className="flex items-center gap-2 mb-3">
        <div className="flex h-6 w-6 items-center justify-center rounded-full bg-primary text-primary-foreground text-xs font-bold">
          {step}
        </div>
        <h3 className="font-semibold">{title}</h3>
      </div>
      <p className="text-sm text-muted-foreground leading-relaxed">{desc}</p>
    </div>
  )
}

function ErrorPanel({ message }: { message: string }) {
  return (
    <div className="mx-auto max-w-2xl py-24 px-6">
      <Card className="border-rose-500/40 bg-rose-500/5">
        <CardContent>
          <h3 className="font-semibold text-base mb-2">분석 실패</h3>
          <p className="text-sm text-muted-foreground">{message}</p>
        </CardContent>
      </Card>
    </div>
  )
}

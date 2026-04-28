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
    <div className="mx-auto max-w-2xl py-32 px-6 text-center">
      <h2 className="text-3xl font-bold tracking-tight mb-4">
        레포 경로를 입력하고 Enter
      </h2>
      <p className="text-muted-foreground leading-relaxed">
        CodeXray는 코드베이스를 읽고 "이게 뭐고, 어떤 상태고, 뭘 먼저 봐야 하는지"를
        한 화면에서 정리합니다.
      </p>
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

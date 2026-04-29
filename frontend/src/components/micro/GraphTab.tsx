import { useTabData } from "@/components/micro/useTabData"

interface DashboardPayload {
  schema_version: number
  html: string
}

interface Props {
  path: string
}

export function GraphTab({ path }: Props) {
  const state = useTabData<DashboardPayload>("dashboard", path)

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

  return (
    <div className="rounded-lg border overflow-hidden bg-white">
      <iframe
        srcDoc={state.data.html}
        sandbox="allow-scripts allow-same-origin"
        title="구조 그래프"
        className="w-full"
        style={{ height: "calc(100vh - 240px)", minHeight: "640px", border: 0 }}
      />
    </div>
  )
}

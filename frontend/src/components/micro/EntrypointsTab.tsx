import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { useTabData } from "@/components/micro/useTabData"

interface Entrypoint {
  path: string
  kind: string
  reason?: string
}

interface EntrypointsPayload {
  schema_version: number
  entrypoints: Entrypoint[]
}

const KIND_LABEL: Record<string, string> = {
  python_main: "Python main",
  python_typer: "Typer CLI",
  python_argparse: "argparse CLI",
  fastapi: "FastAPI",
  flask: "Flask",
  starlette: "Starlette",
  unity_lifecycle: "Unity 라이프사이클",
  node_main: "Node main",
  cargo_bin: "Cargo binary",
  go_main: "Go main",
}

interface Props {
  path: string
}

export function EntrypointsTab({ path }: Props) {
  const state = useTabData<EntrypointsPayload>("entrypoints", path)

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

  const groups = state.data.entrypoints.reduce<Record<string, Entrypoint[]>>((acc, ep) => {
    if (!acc[ep.kind]) acc[ep.kind] = []
    acc[ep.kind].push(ep)
    return acc
  }, {})

  return (
    <div className="space-y-4">
      <Card>
        <CardContent>
          <div className="flex items-baseline gap-3 mb-4">
            <div className="text-3xl font-bold tabular-nums">
              {state.data.entrypoints.length}
            </div>
            <div className="text-sm text-muted-foreground">감지된 진입점</div>
          </div>
          {state.data.entrypoints.length === 0 ? (
            <p className="text-sm text-muted-foreground">감지된 진입점이 없습니다.</p>
          ) : (
            <div className="space-y-4">
              {Object.entries(groups).map(([kind, eps]) => (
                <div key={kind}>
                  <div className="flex items-center gap-2 mb-2">
                    <Badge variant="secondary" className="text-[10px] uppercase">
                      {KIND_LABEL[kind] || kind}
                    </Badge>
                    <span className="text-xs text-muted-foreground tabular-nums">
                      {eps.length}개
                    </span>
                  </div>
                  <ul className="space-y-1.5">
                    {eps.map((ep, i) => (
                      <li
                        key={`${ep.path}-${i}`}
                        className="font-mono text-xs text-muted-foreground pl-4 border-l-2"
                      >
                        {ep.path}
                        {ep.reason && (
                          <span className="text-muted-foreground/70 ml-2">— {ep.reason}</span>
                        )}
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

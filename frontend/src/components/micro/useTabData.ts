import { useEffect, useState } from "react"
import { fetchTab } from "@/lib/api"

type State<T> =
  | { kind: "loading" }
  | { kind: "error"; message: string }
  | { kind: "done"; data: T }

export function useTabData<T>(tab: string, path: string): State<T> {
  const [state, setState] = useState<State<T>>({ kind: "loading" })
  useEffect(() => {
    let cancelled = false
    setState({ kind: "loading" })
    fetchTab<T>(tab, path)
      .then((data) => {
        if (!cancelled) setState({ kind: "done", data })
      })
      .catch((err: Error) => {
        if (!cancelled) setState({ kind: "error", message: err.message })
      })
    return () => {
      cancelled = true
    }
  }, [tab, path])
  return state
}

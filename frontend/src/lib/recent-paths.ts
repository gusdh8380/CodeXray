const KEY = "codexray.recentPaths.v2"
const MAX = 5

export function getRecentPaths(): string[] {
  try {
    const raw = localStorage.getItem(KEY)
    if (!raw) return []
    const parsed = JSON.parse(raw)
    return Array.isArray(parsed) ? parsed.filter((s) => typeof s === "string") : []
  } catch {
    return []
  }
}

export function rememberPath(path: string): void {
  if (!path) return
  const existing = getRecentPaths().filter((p) => p !== path)
  const next = [path, ...existing].slice(0, MAX)
  try {
    localStorage.setItem(KEY, JSON.stringify(next))
  } catch {
    /* ignore quota errors */
  }
}

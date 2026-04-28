const KEY = "codexray.theme.v2"

export type Theme = "light" | "dark"

export function readTheme(): Theme {
  const stored = localStorage.getItem(KEY)
  if (stored === "light" || stored === "dark") return stored
  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light"
}

export function applyTheme(theme: Theme): void {
  const root = document.documentElement
  if (theme === "dark") root.classList.add("dark")
  else root.classList.remove("dark")
  localStorage.setItem(KEY, theme)
}

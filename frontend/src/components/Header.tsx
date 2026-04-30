import { useEffect, useState } from "react"
import { FolderOpen, Moon, Sun } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { applyTheme, readTheme, type Theme } from "@/lib/theme"
import { browseFolder } from "@/lib/api"
import { getRecentPaths } from "@/lib/recent-paths"

interface HeaderProps {
  path: string
  onPathChange: (path: string) => void
  onSubmit: (path: string) => void
  isAnalyzing: boolean
}

export function Header({ path, onPathChange, onSubmit, isAnalyzing }: HeaderProps) {
  const [theme, setTheme] = useState<Theme>("light")
  const [recents, setRecents] = useState<string[]>([])

  useEffect(() => {
    const initial = readTheme()
    setTheme(initial)
    applyTheme(initial)
    setRecents(getRecentPaths())
  }, [])

  function toggleTheme() {
    const next: Theme = theme === "dark" ? "light" : "dark"
    setTheme(next)
    applyTheme(next)
  }

  async function handleBrowse() {
    const result = await browseFolder()
    if (result.path) {
      onPathChange(result.path)
    }
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (path.trim() && !isAnalyzing) onSubmit(path.trim())
  }

  return (
    <header className="border-b bg-card/50 backdrop-blur sticky top-0 z-10">
      <div className="mx-auto max-w-6xl px-6 py-4 flex items-center gap-4">
        <div className="flex flex-col">
          <h1 className="text-xl font-bold tracking-tight">CodeXray</h1>
          <p className="text-xs text-muted-foreground">로컬 코드베이스 분석</p>
        </div>
        <form onSubmit={handleSubmit} className="flex-1 flex items-center gap-2">
          <Input
            value={path}
            onChange={(e) => onPathChange(e.target.value)}
            placeholder="프로젝트 경로를 입력하고 Enter"
            className="flex-1"
            disabled={isAnalyzing}
            aria-label="프로젝트 경로"
          />
          <Button
            type="button"
            variant="outline"
            size="icon"
            onClick={handleBrowse}
            disabled={isAnalyzing}
            aria-label="폴더 선택"
            title="폴더 선택 (macOS)"
          >
            <FolderOpen className="h-4 w-4" />
          </Button>
          {recents.length > 0 && (
            <select
              className="h-10 rounded-md border bg-background px-2 text-sm"
              value=""
              onChange={(e) => {
                if (e.target.value) {
                  onPathChange(e.target.value)
                  onSubmit(e.target.value)
                }
              }}
              disabled={isAnalyzing}
              aria-label="최근 경로"
            >
              <option value="">최근 경로</option>
              {recents.map((p) => (
                <option key={p} value={p}>
                  {p}
                </option>
              ))}
            </select>
          )}
        </form>
        <Button variant="ghost" size="icon" onClick={toggleTheme} aria-label="테마 전환">
          {theme === "dark" ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
        </Button>
      </div>
    </header>
  )
}

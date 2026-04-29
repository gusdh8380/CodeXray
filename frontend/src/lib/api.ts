export interface LanguageRow {
  language: string
  files: number
  loc: number
  share: number
}

export interface CoupledRow {
  path: string
  fan_in: number
  fan_out: number
  external_fan_out: number
  coupling: number
}

export interface EntrypointRow {
  path: string
  kind: string
}

export interface QualityDimensionRow {
  name: string
  grade: string
  score: number | null
}

export interface HotspotRow {
  path: string
  priority: number
  changes: number
  coupling: number
  category: string
}

export interface SectionDetails {
  languages?: LanguageRow[]
  top_coupled?: CoupledRow[]
  entrypoints?: EntrypointRow[]
  is_dag?: boolean
  dimensions?: QualityDimensionRow[]
  hotspots?: HotspotRow[]
}

export interface BriefingSection {
  id: string
  title: string
  narrative: string
  metrics?: { label: string; value: string }[]
  details?: SectionDetails
  deep_link?: { label: string; tab: string }
}

export interface AxisBreakdownItem {
  label: string
  delta: number
  satisfied: boolean
  hint: string
}

export interface VibeAxis {
  name: string
  score: number
  label: string
  weaknesses: string[]
  breakdown?: AxisBreakdownItem[]
}

export interface TimelineEntry {
  day: number
  type: "code" | "spec" | "agent" | "validation" | "retro"
  title: string
  evidence?: string
}

export interface IntentAlignment {
  narrative: string
  intent_present: boolean
}

export interface VibeInsights {
  detected: boolean
  axes?: VibeAxis[]
  timeline?: TimelineEntry[]
  ai_narrative?: string
  starter_guide?: { action: string; reason: string }[]
  intent_alignment?: IntentAlignment
}

export interface NextAction {
  action: string
  reason: string
  evidence: string
  ai_prompt?: string
}

export interface BriefingPayload {
  schema_version: number
  path: string
  what: BriefingSection
  how_built: BriefingSection
  current_state: BriefingSection
  vibe_insights: VibeInsights
  next_actions: NextAction[]
  ai_used: boolean
}

export interface BriefingJobStatus {
  job_id: string
  status: "running" | "completed" | "failed" | "cancelled"
  step: string
  progress: number
  result?: BriefingPayload
  error?: string
}

const API_BASE = ""

export async function startBriefing(path: string): Promise<{ job_id: string }> {
  const res = await fetch(`${API_BASE}/api/briefing`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ path }),
  })
  if (!res.ok) throw new Error(`briefing start failed: ${res.status}`)
  return res.json()
}

export async function getBriefingStatus(jobId: string): Promise<BriefingJobStatus> {
  const res = await fetch(`${API_BASE}/api/briefing/status/${jobId}`)
  if (!res.ok) throw new Error(`briefing status failed: ${res.status}`)
  return res.json()
}

export interface BrowseFolderResult {
  path?: string
  cancelled?: boolean
  error?: string
}

export async function browseFolder(): Promise<BrowseFolderResult> {
  const res = await fetch(`${API_BASE}/api/browse-folder`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
  })
  if (!res.ok) {
    try {
      const body = await res.json()
      return { error: body?.error || `폴더 선택 실패: ${res.status}` }
    } catch {
      return { error: `폴더 선택 실패: ${res.status}` }
    }
  }
  return res.json()
}

export async function fetchTab<T = unknown>(tab: string, path: string): Promise<T> {
  const res = await fetch(`${API_BASE}/api/${tab}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ path }),
  })
  if (!res.ok) {
    let message = `${tab} 분석 실패: ${res.status}`
    try {
      const body = await res.json()
      if (body?.error) message = body.error
    } catch {
      /* keep default */
    }
    throw new Error(message)
  }
  return res.json()
}

export async function pollBriefing(
  path: string,
  onProgress: (status: BriefingJobStatus) => void,
  signal?: AbortSignal,
): Promise<BriefingPayload> {
  const { job_id } = await startBriefing(path)
  while (true) {
    if (signal?.aborted) throw new Error("aborted")
    const status = await getBriefingStatus(job_id)
    onProgress(status)
    if (status.status === "completed" && status.result) return status.result
    if (status.status === "failed") throw new Error(status.error || "briefing failed")
    if (status.status === "cancelled") throw new Error("briefing cancelled")
    await new Promise((r) => setTimeout(r, 2000))
  }
}

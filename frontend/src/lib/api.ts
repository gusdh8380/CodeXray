export interface BriefingSection {
  id: string
  title: string
  narrative: string
  metrics?: { label: string; value: string }[]
  deep_link?: { label: string; tab: string }
}

export interface VibeAxis {
  name: string
  score: number
  label: string
  weaknesses: string[]
}

export interface TimelineEntry {
  day: number
  type: "code" | "spec" | "agent" | "validation" | "retro"
  title: string
  evidence?: string
}

export interface VibeInsights {
  detected: boolean
  axes?: VibeAxis[]
  timeline?: TimelineEntry[]
  ai_narrative?: string
  starter_guide?: { action: string; reason: string }[]
}

export interface NextAction {
  action: string
  reason: string
  evidence: string
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

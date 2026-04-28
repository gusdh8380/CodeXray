import { Progress } from "@/components/ui/progress"
import { Loader2 } from "lucide-react"
import type { BriefingJobStatus } from "@/lib/api"

interface Props {
  status: BriefingJobStatus | null
}

export function BriefingProgress({ status }: Props) {
  const step = status?.step ?? "분석 시작 중..."
  const progress = Math.round((status?.progress ?? 0) * 100)
  return (
    <div className="mx-auto max-w-2xl py-24 px-6 text-center space-y-6">
      <div className="flex justify-center">
        <Loader2 className="h-10 w-10 animate-spin text-primary" />
      </div>
      <div>
        <p className="text-lg font-medium">{step}</p>
        <p className="text-sm text-muted-foreground mt-2">
          AI가 코드베이스를 읽고 해석하고 있습니다. 잠시 기다려 주세요.
        </p>
      </div>
      <Progress value={progress} className="max-w-md mx-auto" />
      <p className="text-xs text-muted-foreground">{progress}%</p>
    </div>
  )
}

import { ArrowRight } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"
import { cn } from "@/lib/utils"

interface Props {
  eyebrow: string
  title: string
  narrative: string
  metrics?: { label: string; value: string }[]
  deepLink?: { label: string; tab: string }
  variant?: "hero" | "default" | "highlight"
  children?: React.ReactNode
}

export function SectionShell({
  eyebrow,
  title,
  narrative,
  metrics,
  deepLink,
  variant = "default",
  children,
}: Props) {
  return (
    <Card
      className={cn(
        "border-2",
        variant === "hero" && "border-primary/20 bg-gradient-to-br from-card to-muted/30",
        variant === "highlight" && "border-amber-500/30",
      )}
    >
      <CardContent className="space-y-4 px-8 py-2">
        <div className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
          {eyebrow}
        </div>
        <h2
          className={cn(
            "font-bold tracking-tight",
            variant === "hero" ? "text-4xl" : "text-2xl",
          )}
        >
          {title}
        </h2>
        <p
          className={cn(
            "leading-relaxed text-foreground/90",
            variant === "hero" ? "text-lg" : "text-base",
          )}
        >
          {narrative}
        </p>
        {metrics && metrics.length > 0 && (
          <div className="flex flex-wrap gap-6 pt-2">
            {metrics.map((m) => (
              <div key={m.label}>
                <div className="text-2xl font-bold">{m.value}</div>
                <div className="text-xs text-muted-foreground uppercase tracking-wide">
                  {m.label}
                </div>
              </div>
            ))}
          </div>
        )}
        {children}
        {deepLink && (
          <button
            type="button"
            className="inline-flex items-center gap-1 text-sm text-primary hover:underline pt-2"
          >
            {deepLink.label} <ArrowRight className="h-3 w-3" />
          </button>
        )}
      </CardContent>
    </Card>
  )
}

import { useState } from "react"
import { ChevronDown, ChevronRight } from "lucide-react"
import { QualityTab } from "@/components/micro/QualityTab"
import { HotspotsTab } from "@/components/micro/HotspotsTab"
import { InventoryTab } from "@/components/micro/InventoryTab"
import { MetricsTab } from "@/components/micro/MetricsTab"
import { EntrypointsTab } from "@/components/micro/EntrypointsTab"
import { cn } from "@/lib/utils"

const TABS = [
  { id: "quality", label: "품질" },
  { id: "hotspots", label: "Hotspot" },
  { id: "metrics", label: "결합도" },
  { id: "inventory", label: "파일 분포" },
  { id: "entrypoints", label: "진입점" },
] as const

type TabId = (typeof TABS)[number]["id"]

interface Props {
  path: string
}

export function MicroAnalysisArea({ path }: Props) {
  const [open, setOpen] = useState(false)
  const [active, setActive] = useState<TabId>("quality")

  return (
    <section className="mt-12 border-t pt-8">
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        className="flex items-center gap-2 text-lg font-semibold tracking-tight hover:text-primary transition-colors"
      >
        {open ? <ChevronDown className="h-5 w-5" /> : <ChevronRight className="h-5 w-5" />}
        상세 분석
      </button>
      {open && (
        <div className="mt-6 space-y-6">
          <nav className="flex gap-2 border-b">
            {TABS.map((tab) => (
              <button
                key={tab.id}
                type="button"
                onClick={() => setActive(tab.id)}
                className={cn(
                  "relative px-4 py-2 text-sm font-medium transition-colors",
                  active === tab.id
                    ? "text-primary"
                    : "text-muted-foreground hover:text-foreground",
                )}
              >
                {tab.label}
                {active === tab.id && (
                  <span className="absolute inset-x-0 -bottom-px h-0.5 bg-primary" />
                )}
              </button>
            ))}
          </nav>
          <div>
            {active === "quality" && <QualityTab path={path} />}
            {active === "hotspots" && <HotspotsTab path={path} />}
            {active === "metrics" && <MetricsTab path={path} />}
            {active === "inventory" && <InventoryTab path={path} />}
            {active === "entrypoints" && <EntrypointsTab path={path} />}
          </div>
        </div>
      )}
    </section>
  )
}

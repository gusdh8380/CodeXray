import { useEffect, useRef } from "react"
import * as d3 from "d3"
import type { ArchitectureView } from "@/lib/architecture"
import { HOTSPOT_CATEGORY_COLOR } from "@/lib/architecture"

interface Props {
  data: ArchitectureView
  height?: number
}

interface LeafDatum {
  type: "leaf"
  path: string
  label: string
  module: string
  category: string
  coupling: number
}

interface ModuleDatum {
  type: "module"
  name: string
  children: LeafDatum[]
}

interface RootDatum {
  type: "root"
  name: string
  children: ModuleDatum[]
}

type AnyDatum = LeafDatum | ModuleDatum | RootDatum

export function BundlingView({ data, height = 760 }: Props) {
  const svgRef = useRef<SVGSVGElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const svg = d3.select(svgRef.current!)
    const container = containerRef.current!
    svg.selectAll("*").remove()
    const width = container.clientWidth || 800

    const moduleColor = new Map(data.modules.map((m) => [m.name, m.color]))

    // Build hierarchy: root -> modules -> leaves (sorted by coupling within module)
    const byModule = d3.group(data.nodes, (n) => n.module)
    const moduleChildren: ModuleDatum[] = Array.from(byModule.entries())
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([name, items]) => ({
        type: "module" as const,
        name,
        children: items
          .slice()
          .sort((a, b) => b.coupling - a.coupling)
          .map<LeafDatum>((n) => ({
            type: "leaf",
            path: n.path,
            label: n.label,
            module: n.module,
            category: n.category,
            coupling: n.coupling,
          })),
      }))
    const rootData: RootDatum = { type: "root", name: "root", children: moduleChildren }

    const radius = Math.min(width, height) / 2 - 80
    const cx = width / 2
    const cy = height / 2

    type Node = d3.HierarchyPointNode<AnyDatum>
    const root = d3
      .hierarchy<AnyDatum>(rootData, (d) =>
        d.type === "root" || d.type === "module" ? (d as RootDatum | ModuleDatum).children : null,
      )
      .sum(() => 1)
    const cluster = d3.cluster<AnyDatum>().size([360, radius])
    cluster(root)
    const positioned = root as Node

    // Build path index from full file path → cluster node
    const leafByPath = new Map<string, Node>()
    positioned.eachBefore((node) => {
      if (node.data.type === "leaf") {
        leafByPath.set((node.data as LeafDatum).path, node)
      }
    })

    // Polar to cartesian helper
    function project(angle: number, r: number): [number, number] {
      const rad = ((angle - 90) * Math.PI) / 180
      return [cx + Math.cos(rad) * r, cy + Math.sin(rad) * r]
    }

    const lineRadial = d3
      .lineRadial<Node>()
      .curve(d3.curveBundle.beta(0.85))
      .radius((d) => d.y)
      .angle((d) => (d.x * Math.PI) / 180)

    // Compute the path through the tree between two leaves (LCA path)
    function pathBetween(a: Node, b: Node): Node[] {
      const ancestorsA = a.ancestors()
      const ancestorsB = b.ancestors()
      const setB = new Set(ancestorsB)
      let lca: Node | null = null
      for (const node of ancestorsA) {
        if (setB.has(node)) {
          lca = node
          break
        }
      }
      if (!lca) return [a, b]
      const upPath: Node[] = []
      let cur: Node | null = a
      while (cur && cur !== lca) {
        upPath.push(cur)
        cur = cur.parent
      }
      upPath.push(lca)
      const downPath: Node[] = []
      cur = b
      while (cur && cur !== lca) {
        downPath.push(cur)
        cur = cur.parent
      }
      downPath.reverse()
      return [...upPath, ...downPath]
    }

    const zoomLayer = svg.append("g").attr("class", "zoom-layer")

    const zoom = d3
      .zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.4, 4])
      .on("zoom", (event) => zoomLayer.attr("transform", event.transform.toString()))
    svg.call(zoom).on("dblclick.zoom", null)

    // Edges layer
    const edgesG = zoomLayer.append("g").attr("class", "bundle-edges")
    const edges = data.edges
      .map((e) => {
        const a = leafByPath.get(e.from)
        const b = leafByPath.get(e.to)
        if (!a || !b) return null
        return { from: e.from, to: e.to, points: pathBetween(a, b) }
      })
      .filter((e): e is { from: string; to: string; points: Node[] } => Boolean(e))

    const edgePaths = edgesG
      .selectAll<SVGPathElement, (typeof edges)[number]>("path")
      .data(edges)
      .enter()
      .append("path")
      .attr("d", (d) => lineRadial(d.points))
      .attr("fill", "none")
      .attr("stroke", "currentColor")
      .attr("stroke-opacity", 0.16)
      .attr("stroke-width", 0.8)
      .attr("transform", `translate(${cx},${cy})`)

    // Module arcs (bands at outer radius)
    const arcsG = zoomLayer.append("g").attr("class", "bundle-arcs")
    const arcInner = radius + 4
    const arcOuter = radius + 12
    positioned.children?.forEach((moduleNode) => {
      if (!moduleNode.children || moduleNode.children.length === 0) return
      const startAngle = d3.min(moduleNode.children, (c) => c.x) ?? 0
      const endAngle = d3.max(moduleNode.children, (c) => c.x) ?? 0
      const arc = d3
        .arc<unknown>()
        .innerRadius(arcInner)
        .outerRadius(arcOuter)
        .startAngle(((startAngle - 1.5) * Math.PI) / 180)
        .endAngle(((endAngle + 1.5) * Math.PI) / 180)
      const moduleName = (moduleNode.data as ModuleDatum).name
      arcsG
        .append("path")
        .attr("d", arc({}))
        .attr("transform", `translate(${cx},${cy})`)
        .attr("fill", moduleColor.get(moduleName) || "#94a3b8")
        .attr("opacity", 0.65)
        .style("cursor", "pointer")
        .append("title")
        .text(`${moduleName} (${moduleNode.children.length})`)

      const midAngle = (startAngle + endAngle) / 2
      const labelRadius = arcOuter + 14
      const [lx, ly] = project(midAngle, labelRadius)
      const rotate =
        midAngle > 180
          ? `rotate(${midAngle - 180}, ${lx}, ${ly})`
          : `rotate(${midAngle}, ${lx}, ${ly})`
      arcsG
        .append("text")
        .attr("x", lx)
        .attr("y", ly)
        .attr("transform", rotate)
        .attr("text-anchor", midAngle > 180 ? "end" : "start")
        .attr("font-size", 11)
        .attr("font-weight", 600)
        .attr("fill", moduleColor.get(moduleName) || "#374151")
        .text(moduleName)
    })

    // Leaf dots (placed at outer ring)
    const leafG = zoomLayer.append("g").attr("class", "bundle-leaves")
    const leaves = positioned.leaves()
    const dotSel = leafG
      .selectAll<SVGCircleElement, Node>("circle")
      .data(leaves)
      .enter()
      .append("circle")
      .attr("transform", `translate(${cx},${cy})`)
      .attr("cx", (d) => {
        const [x] = project(d.x, d.y)
        return x - cx
      })
      .attr("cy", (d) => {
        const [, y] = project(d.x, d.y)
        return y - cy
      })
      .attr("r", (d) => Math.min(7, Math.log((d.data as LeafDatum).coupling + 1) * 1.6 + 2))
      .attr("fill", (d) => HOTSPOT_CATEGORY_COLOR[(d.data as LeafDatum).category] || "#9ca3af")
      .attr("stroke", (d) => moduleColor.get((d.data as LeafDatum).module) || "#374151")
      .attr("stroke-width", 1.2)
      .style("cursor", "pointer")

    dotSel
      .append("title")
      .text(
        (d) =>
          `${(d.data as LeafDatum).path}\n${(d.data as LeafDatum).module} · coupling=${(d.data as LeafDatum).coupling}`,
      )

    // Click highlight: dim all edges, highlight ones touching this leaf
    let active: string | null = null
    function applyHighlight(path: string | null) {
      active = path
      if (!path) {
        edgePaths.attr("stroke-opacity", 0.16).attr("stroke-width", 0.8).attr("stroke", "currentColor")
        dotSel.style("opacity", 1)
        return
      }
      edgePaths
        .attr("stroke-opacity", (e) => (e.from === path || e.to === path ? 0.7 : 0.04))
        .attr("stroke-width", (e) => (e.from === path || e.to === path ? 1.4 : 0.6))
        .attr("stroke", (e) => {
          if (e.from === path) return "#dc2626" // outgoing — red
          if (e.to === path) return "#2563eb" // incoming — blue
          return "currentColor"
        })
      dotSel.style("opacity", (d) => {
        const leafPath = (d.data as LeafDatum).path
        if (leafPath === path) return 1
        const isNeighbor = edges.some(
          (e) =>
            (e.from === path && e.to === leafPath) || (e.to === path && e.from === leafPath),
        )
        return isNeighbor ? 1 : 0.18
      })
    }
    dotSel.on("click", (event, d) => {
      event.stopPropagation()
      const path = (d.data as LeafDatum).path
      applyHighlight(active === path ? null : path)
    })
    svg.on("click", () => applyHighlight(null))
  }, [data, height])

  return (
    <div ref={containerRef} className="relative">
      <svg
        ref={svgRef}
        width="100%"
        height={height}
        className="rounded-lg border bg-card"
        style={{ cursor: "grab" }}
      />
      <div className="absolute bottom-3 left-3 text-[11px] text-muted-foreground bg-card/80 backdrop-blur rounded px-2 py-1 border">
        노드 클릭: <span className="text-rose-500">→ 의존 (out)</span> /{" "}
        <span className="text-blue-500">← 의존받음 (in)</span>
      </div>
    </div>
  )
}

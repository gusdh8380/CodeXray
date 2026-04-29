import { useEffect, useRef } from "react"
import * as d3 from "d3"
import type { ArchEdge, ArchNode, ArchitectureView } from "@/lib/architecture"
import { HOTSPOT_CATEGORY_COLOR } from "@/lib/architecture"

interface Props {
  data: ArchitectureView
  height?: number
}

interface Positioned extends ArchNode {
  x: number
  y: number
  r: number
}

const LAYER_PADDING = 80
const NODE_GAP = 14

export function LayeredView({ data, height = 720 }: Props) {
  const svgRef = useRef<SVGSVGElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const svg = d3.select(svgRef.current!)
    const container = containerRef.current!
    svg.selectAll("*").remove()
    const width = container.clientWidth || 800

    const moduleColor = new Map(data.modules.map((m) => [m.name, m.color]))

    // Group by layer
    const layerCount = data.layer_count || 1
    const byLayer = new Map<number, ArchNode[]>()
    for (const node of data.nodes) {
      if (!byLayer.has(node.layer)) byLayer.set(node.layer, [])
      byLayer.get(node.layer)!.push(node)
    }

    // Sort each layer's nodes by module then coupling so module clusters stay together horizontally
    for (const [layer, list] of byLayer) {
      list.sort((a, b) => {
        if (a.module !== b.module) return a.module.localeCompare(b.module)
        return b.coupling - a.coupling
      })
      byLayer.set(layer, list)
    }

    // Vertical positions: layer 0 at the bottom, highest layer at the top.
    // (Visual convention: callers above their callees.)
    const usableHeight = height - LAYER_PADDING * 2
    const layerY = (layer: number) =>
      layerCount <= 1
        ? height / 2
        : LAYER_PADDING + usableHeight - (layer / Math.max(1, layerCount - 1)) * usableHeight

    // Horizontal positions per layer: spread evenly with module-aware spacing
    const positioned = new Map<string, Positioned>()
    for (const [layer, list] of byLayer) {
      const innerWidth = width - 80
      const step = list.length > 1 ? innerWidth / (list.length - 1) : 0
      list.forEach((node, idx) => {
        const x = list.length === 1 ? width / 2 : 40 + idx * step
        const y = layerY(layer)
        positioned.set(node.path, {
          ...node,
          x,
          y,
          r: Math.min(20, Math.log(node.coupling + 1) * 3 + 4),
        })
      })
    }

    const zoomLayer = svg.append("g").attr("class", "zoom-layer")

    const zoom = d3
      .zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.3, 4])
      .on("zoom", (event) => zoomLayer.attr("transform", event.transform.toString()))
    svg.call(zoom).on("dblclick.zoom", null)

    // Layer dividers and labels
    for (let layer = 0; layer < layerCount; layer++) {
      const y = layerY(layer)
      zoomLayer
        .append("line")
        .attr("x1", 20)
        .attr("x2", width - 20)
        .attr("y1", y + 30)
        .attr("y2", y + 30)
        .attr("stroke", "currentColor")
        .attr("stroke-opacity", 0.06)
        .attr("stroke-dasharray", "2 4")
      zoomLayer
        .append("text")
        .attr("x", 24)
        .attr("y", y - NODE_GAP)
        .attr("font-size", 10)
        .attr("fill", "currentColor")
        .attr("opacity", 0.45)
        .text(`레이어 ${layer}`)
    }

    // Edges (curved)
    const linkPath = (e: ArchEdge): string | null => {
      const a = positioned.get(e.from)
      const b = positioned.get(e.to)
      if (!a || !b) return null
      const dx = b.x - a.x
      const dy = b.y - a.y
      const cx = a.x + dx / 2
      const cy = a.y + dy / 2 + Math.abs(dx) * 0.05
      return `M ${a.x},${a.y} Q ${cx},${cy} ${b.x},${b.y}`
    }

    const link = zoomLayer
      .append("g")
      .selectAll<SVGPathElement, ArchEdge>("path")
      .data(data.edges)
      .enter()
      .append("path")
      .attr("d", (e) => linkPath(e))
      .attr("fill", "none")
      .attr("stroke", "currentColor")
      .attr("stroke-opacity", 0.14)
      .attr("stroke-width", 1)

    const nodeG = zoomLayer
      .append("g")
      .selectAll<SVGGElement, Positioned>("g.node")
      .data(Array.from(positioned.values()))
      .enter()
      .append("g")
      .attr("class", "node")
      .attr("transform", (d) => `translate(${d.x},${d.y})`)
      .style("cursor", "pointer")

    nodeG
      .append("circle")
      .attr("r", (d) => d.r)
      .attr("fill", (d) => HOTSPOT_CATEGORY_COLOR[d.category] || "#9ca3af")
      .attr("stroke", (d) => moduleColor.get(d.module) || "#374151")
      .attr("stroke-width", 2)

    nodeG.append("title").text((d) => `${d.path}\n${d.module} · L${d.layer} · coupling=${d.coupling}`)

    // Top labels
    const topPaths = new Set(
      [...data.nodes]
        .sort((a, b) => b.coupling - a.coupling)
        .slice(0, 12)
        .map((n) => n.path),
    )
    nodeG
      .filter((d) => topPaths.has(d.path))
      .append("text")
      .text((d) => d.label)
      .attr("text-anchor", "middle")
      .attr("y", (d) => d.r + 11)
      .attr("font-size", 10)
      .attr("fill", "currentColor")
      .attr("opacity", 0.85)

    // Highlight neighbors on click
    const adjacency = new Map<string, Set<string>>()
    for (const e of data.edges) {
      if (!adjacency.has(e.from)) adjacency.set(e.from, new Set())
      if (!adjacency.has(e.to)) adjacency.set(e.to, new Set())
      adjacency.get(e.from)!.add(e.to)
      adjacency.get(e.to)!.add(e.from)
    }
    let activePath: string | null = null
    function applyHighlight(path: string | null) {
      activePath = path
      if (!path) {
        nodeG.style("opacity", 1)
        link.attr("stroke-opacity", 0.14)
        return
      }
      const neighbors = adjacency.get(path) ?? new Set()
      nodeG.style("opacity", (d) =>
        d.path === path || neighbors.has(d.path) ? 1 : 0.15,
      )
      link.attr("stroke-opacity", (e) =>
        e.from === path || e.to === path ? 0.6 : 0.04,
      )
    }
    nodeG.on("click", (event, d) => {
      event.stopPropagation()
      applyHighlight(activePath === d.path ? null : d.path)
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
    </div>
  )
}

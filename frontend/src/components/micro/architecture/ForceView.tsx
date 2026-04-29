import { useEffect, useRef } from "react"
import * as d3 from "d3"
import type { ArchEdge, ArchNode, ArchitectureView } from "@/lib/architecture"
import { HOTSPOT_CATEGORY_COLOR } from "@/lib/architecture"

interface SimNode extends ArchNode, d3.SimulationNodeDatum {
  r: number
}

interface SimEdge extends d3.SimulationLinkDatum<SimNode> {
  source: string | SimNode
  target: string | SimNode
}

interface Props {
  data: ArchitectureView
  height?: number
}

export function ForceView({ data, height = 640 }: Props) {
  const svgRef = useRef<SVGSVGElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const svg = d3.select(svgRef.current!)
    const container = containerRef.current!
    svg.selectAll("*").remove()

    const width = container.clientWidth || 800

    const couplings = data.nodes.map((n) => n.coupling).sort((a, b) => a - b)
    const p90 = couplings.length > 1 ? couplings[Math.floor(couplings.length * 0.9)] : 0

    const moduleColor = new Map(data.modules.map((m) => [m.name, m.color]))

    const nodes: SimNode[] = data.nodes.map((n) => ({
      ...n,
      r: Math.log(n.coupling + 1) * 4 + 4,
    }))
    const nodeIds = new Set(nodes.map((n) => n.path))
    const edges: SimEdge[] = data.edges
      .filter((e) => nodeIds.has(e.from) && nodeIds.has(e.to))
      .map((e: ArchEdge) => ({ source: e.from, target: e.to }))

    const zoomLayer = svg.append("g").attr("class", "zoom-layer")

    const zoom = d3
      .zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.2, 4])
      .on("zoom", (event) => {
        zoomLayer.attr("transform", event.transform.toString())
      })
    svg.call(zoom).on("dblclick.zoom", null)

    const link = zoomLayer
      .append("g")
      .selectAll("line")
      .data(edges)
      .enter()
      .append("line")
      .attr("stroke", "currentColor")
      .attr("stroke-opacity", 0.18)
      .attr("stroke-width", 1)

    const node = zoomLayer
      .append("g")
      .selectAll<SVGCircleElement, SimNode>("circle")
      .data(nodes)
      .enter()
      .append("circle")
      .attr("r", (d) => d.r * (d.coupling >= p90 && p90 > 0 ? 1.4 : 1))
      .attr("fill", (d) => HOTSPOT_CATEGORY_COLOR[d.category] || "#9ca3af")
      .attr("stroke", (d) => moduleColor.get(d.module) || "#374151")
      .attr("stroke-width", 2)
      .style("cursor", "pointer")
      .call(
        d3
          .drag<SVGCircleElement, SimNode>()
          .on("start", (event, d) => {
            if (!event.active) sim.alphaTarget(0.3).restart()
            d.fx = d.x
            d.fy = d.y
          })
          .on("drag", (event, d) => {
            d.fx = event.x
            d.fy = event.y
          })
          .on("end", (event, d) => {
            if (!event.active) sim.alphaTarget(0)
            d.fx = null
            d.fy = null
          }),
      )

    node.append("title").text((d) => `${d.path}\n${d.module} · L${d.layer} · coupling=${d.coupling}`)

    // Persistent labels for top-coupling nodes
    const topLabels = [...nodes]
      .sort((a, b) => b.coupling - a.coupling)
      .slice(0, 10)
    const topSet = new Set(topLabels.map((n) => n.path))
    const labelSel = zoomLayer
      .append("g")
      .selectAll<SVGTextElement, SimNode>("text")
      .data(nodes.filter((n) => topSet.has(n.path)))
      .enter()
      .append("text")
      .text((d) => d.label)
      .attr("font-size", 10)
      .attr("fill", "currentColor")
      .attr("text-anchor", "middle")
      .attr("pointer-events", "none")
      .style("opacity", 0.85)

    // Click to highlight neighbors
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
        node.style("opacity", 1).attr("stroke-width", 2)
        link.style("opacity", 0.18)
        labelSel.style("opacity", 0.85)
        return
      }
      const neighbors = adjacency.get(path) ?? new Set()
      node
        .style("opacity", (d) => (d.path === path || neighbors.has(d.path) ? 1 : 0.12))
        .attr("stroke-width", (d) => (d.path === path ? 4 : 2))
      link.style("opacity", (d) => {
        const sourceId = typeof d.source === "string" ? d.source : (d.source as SimNode).path
        const targetId = typeof d.target === "string" ? d.target : (d.target as SimNode).path
        return sourceId === path || targetId === path ? 0.7 : 0.04
      })
      labelSel.style("opacity", (d) => (d.path === path || neighbors.has(d.path) ? 1 : 0.1))
    }

    node.on("click", (event, d) => {
      event.stopPropagation()
      applyHighlight(activePath === d.path ? null : d.path)
    })
    svg.on("click", () => applyHighlight(null))

    const sim = d3
      .forceSimulation<SimNode>(nodes)
      .force(
        "link",
        d3
          .forceLink<SimNode, SimEdge>(edges)
          .id((d) => d.path)
          .distance(50),
      )
      .force("charge", d3.forceManyBody().strength(-160))
      .force("center", d3.forceCenter(width / 2, height / 2))
      .force("x", d3.forceX(width / 2).strength(0.08))
      .force("y", d3.forceY(height / 2).strength(0.08))
      .force(
        "collide",
        d3.forceCollide<SimNode>().radius((d) => d.r + 2),
      )
      .on("tick", () => {
        link
          .attr("x1", (d) => (d.source as SimNode).x ?? 0)
          .attr("y1", (d) => (d.source as SimNode).y ?? 0)
          .attr("x2", (d) => (d.target as SimNode).x ?? 0)
          .attr("y2", (d) => (d.target as SimNode).y ?? 0)
        node.attr("cx", (d) => d.x ?? 0).attr("cy", (d) => d.y ?? 0)
        labelSel.attr("x", (d) => d.x ?? 0).attr("y", (d) => (d.y ?? 0) + d.r + 11)
      })

    return () => {
      sim.stop()
    }
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

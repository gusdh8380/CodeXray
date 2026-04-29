import { useEffect, useRef } from "react"
import * as d3 from "d3"
import type { ArchEdge, ArchNode, ArchitectureView } from "@/lib/architecture"
import { HOTSPOT_CATEGORY_COLOR } from "@/lib/architecture"

interface SimNode extends ArchNode, d3.SimulationNodeDatum {
  r: number
  moduleAnchor: { x: number; y: number }
}

interface SimEdge extends d3.SimulationLinkDatum<SimNode> {
  source: string | SimNode
  target: string | SimNode
}

interface Props {
  data: ArchitectureView
  height?: number
}

// Padding around the convex hull so it visually wraps the cluster
const HULL_PADDING = 24

function hullPath(points: [number, number][]): string {
  if (points.length === 0) return ""
  if (points.length === 1) {
    const [x, y] = points[0]
    return `M ${x - HULL_PADDING},${y} a ${HULL_PADDING},${HULL_PADDING} 0 1,0 ${HULL_PADDING * 2},0 a ${HULL_PADDING},${HULL_PADDING} 0 1,0 ${-HULL_PADDING * 2},0`
  }
  if (points.length === 2) {
    const [a, b] = points
    const dx = b[0] - a[0]
    const dy = b[1] - a[1]
    const dist = Math.sqrt(dx * dx + dy * dy) || 1
    const nx = (-dy / dist) * HULL_PADDING
    const ny = (dx / dist) * HULL_PADDING
    return `M ${a[0] + nx},${a[1] + ny} L ${b[0] + nx},${b[1] + ny} L ${b[0] - nx},${b[1] - ny} L ${a[0] - nx},${a[1] - ny} Z`
  }
  // Convex hull + offset by padding via centroid push
  const hull = d3.polygonHull(points)
  if (!hull) return ""
  const cx = d3.mean(hull, (p) => p[0]) ?? 0
  const cy = d3.mean(hull, (p) => p[1]) ?? 0
  const expanded = hull.map(([x, y]) => {
    const dx = x - cx
    const dy = y - cy
    const len = Math.sqrt(dx * dx + dy * dy) || 1
    return [x + (dx / len) * HULL_PADDING, y + (dy / len) * HULL_PADDING] as [number, number]
  })
  return "M " + expanded.map((p) => p.join(",")).join(" L ") + " Z"
}

export function HullView({ data, height = 720 }: Props) {
  const svgRef = useRef<SVGSVGElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const svg = d3.select(svgRef.current!)
    const container = containerRef.current!
    svg.selectAll("*").remove()
    const width = container.clientWidth || 800

    const moduleColor = new Map(data.modules.map((m) => [m.name, m.color]))

    // Compute initial module anchors in a circle so clusters spread out
    const moduleNames = data.modules.map((m) => m.name)
    const moduleCount = moduleNames.length
    const radius = Math.min(width, height) / 2 - 80
    const centerX = width / 2
    const centerY = height / 2
    const moduleAnchors = new Map<string, { x: number; y: number }>()
    moduleNames.forEach((name, i) => {
      if (moduleCount === 1) {
        moduleAnchors.set(name, { x: centerX, y: centerY })
        return
      }
      const angle = (i / moduleCount) * Math.PI * 2 - Math.PI / 2
      moduleAnchors.set(name, {
        x: centerX + Math.cos(angle) * radius,
        y: centerY + Math.sin(angle) * radius,
      })
    })

    const nodes: SimNode[] = data.nodes.map((n) => ({
      ...n,
      r: Math.log(n.coupling + 1) * 3 + 4,
      moduleAnchor: moduleAnchors.get(n.module) ?? { x: centerX, y: centerY },
      x: (moduleAnchors.get(n.module)?.x ?? centerX) + (Math.random() - 0.5) * 30,
      y: (moduleAnchors.get(n.module)?.y ?? centerY) + (Math.random() - 0.5) * 30,
    }))
    const nodeIds = new Set(nodes.map((n) => n.path))
    const edges: SimEdge[] = data.edges
      .filter((e) => nodeIds.has(e.from) && nodeIds.has(e.to))
      .map((e: ArchEdge) => ({ source: e.from, target: e.to }))

    const zoomLayer = svg.append("g").attr("class", "zoom-layer")

    const zoom = d3
      .zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.2, 4])
      .on("zoom", (event) => zoomLayer.attr("transform", event.transform.toString()))
    svg.call(zoom).on("dblclick.zoom", null)

    // Hull layer (rendered first so nodes draw on top)
    const hullG = zoomLayer.append("g").attr("class", "hulls")
    const hullLabelsG = zoomLayer.append("g").attr("class", "hull-labels")

    const link = zoomLayer
      .append("g")
      .selectAll<SVGLineElement, SimEdge>("line")
      .data(edges)
      .enter()
      .append("line")
      .attr("stroke", "currentColor")
      .attr("stroke-opacity", 0.12)
      .attr("stroke-width", 1)

    const node = zoomLayer
      .append("g")
      .selectAll<SVGCircleElement, SimNode>("circle")
      .data(nodes)
      .enter()
      .append("circle")
      .attr("r", (d) => d.r)
      .attr("fill", (d) => HOTSPOT_CATEGORY_COLOR[d.category] || "#9ca3af")
      .attr("stroke", (d) => moduleColor.get(d.module) || "#374151")
      .attr("stroke-width", 1.5)
      .style("cursor", "pointer")
      .call(
        d3
          .drag<SVGCircleElement, SimNode>()
          .on("start", (event, d) => {
            if (!event.active) sim.alphaTarget(0.2).restart()
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

    // Highlight on hull/node interaction
    let activeModule: string | null = null
    let activePath: string | null = null

    const adjacency = new Map<string, Set<string>>()
    for (const e of data.edges) {
      if (!adjacency.has(e.from)) adjacency.set(e.from, new Set())
      if (!adjacency.has(e.to)) adjacency.set(e.to, new Set())
      adjacency.get(e.from)!.add(e.to)
      adjacency.get(e.to)!.add(e.from)
    }

    function updateHighlight() {
      if (!activeModule && !activePath) {
        node.style("opacity", 1)
        link.attr("stroke-opacity", 0.12)
        hullG.selectAll("path").style("opacity", 0.18)
        return
      }
      const moduleSet = activeModule
        ? new Set(nodes.filter((n) => n.module === activeModule).map((n) => n.path))
        : null
      const neighbors = activePath ? adjacency.get(activePath) ?? new Set() : new Set()
      node.style("opacity", (d) => {
        const inModule = moduleSet?.has(d.path) ?? false
        const isNode = activePath ? d.path === activePath || neighbors.has(d.path) : false
        return inModule || isNode ? 1 : 0.13
      })
      link.attr("stroke-opacity", (e) => {
        const sourceId = typeof e.source === "string" ? e.source : (e.source as SimNode).path
        const targetId = typeof e.target === "string" ? e.target : (e.target as SimNode).path
        if (activePath && (sourceId === activePath || targetId === activePath)) return 0.6
        if (
          moduleSet &&
          ((moduleSet.has(sourceId) && moduleSet.has(targetId)) ||
            moduleSet.has(sourceId) ||
            moduleSet.has(targetId))
        )
          return 0.35
        return 0.04
      })
      hullG
        .selectAll<SVGPathElement, string>("path")
        .style("opacity", (d) => (activeModule ? (d === activeModule ? 0.4 : 0.05) : 0.18))
    }

    node.on("click", (event, d) => {
      event.stopPropagation()
      activeModule = null
      activePath = activePath === d.path ? null : d.path
      updateHighlight()
    })
    svg.on("click", () => {
      activeModule = null
      activePath = null
      updateHighlight()
    })

    const sim = d3
      .forceSimulation<SimNode>(nodes)
      .force(
        "link",
        d3
          .forceLink<SimNode, SimEdge>(edges)
          .id((d) => d.path)
          .distance(46)
          .strength(0.4),
      )
      .force("charge", d3.forceManyBody<SimNode>().strength(-90))
      .force(
        "x",
        d3.forceX<SimNode>((d) => d.moduleAnchor.x).strength(0.18),
      )
      .force(
        "y",
        d3.forceY<SimNode>((d) => d.moduleAnchor.y).strength(0.18),
      )
      .force(
        "collide",
        d3.forceCollide<SimNode>().radius((d) => d.r + 2),
      )
      .on("tick", tick)

    function tick() {
      link
        .attr("x1", (d) => (d.source as SimNode).x ?? 0)
        .attr("y1", (d) => (d.source as SimNode).y ?? 0)
        .attr("x2", (d) => (d.target as SimNode).x ?? 0)
        .attr("y2", (d) => (d.target as SimNode).y ?? 0)
      node.attr("cx", (d) => d.x ?? 0).attr("cy", (d) => d.y ?? 0)
      drawHulls()
    }

    function drawHulls() {
      const groups = d3.group(nodes, (n) => n.module)
      const hullData = Array.from(groups.entries()).map(([name, items]) => {
        const points = items.map((n) => [n.x ?? 0, n.y ?? 0] as [number, number])
        const path = hullPath(points)
        const cx = d3.mean(items, (n) => n.x ?? 0) ?? 0
        const cy = d3.mean(items, (n) => n.y ?? 0) ?? 0
        return { name, path, cx, cy, count: items.length }
      })

      const hullSel = hullG
        .selectAll<SVGPathElement, { name: string; path: string }>("path")
        .data(hullData, (d) => d.name)
      hullSel.exit().remove()
      const hullEnter = hullSel
        .enter()
        .append("path")
        .attr("fill", (d) => moduleColor.get(d.name) || "#94a3b8")
        .attr("stroke", (d) => moduleColor.get(d.name) || "#94a3b8")
        .attr("stroke-width", 1.5)
        .attr("stroke-linejoin", "round")
        .style("opacity", 0.18)
        .style("cursor", "pointer")
        .on("click", (event, d) => {
          event.stopPropagation()
          activePath = null
          activeModule = activeModule === d.name ? null : d.name
          updateHighlight()
        })
      hullEnter.append("title").text((d) => d.name)
      hullEnter.merge(hullSel).attr("d", (d) => d.path)

      const labelSel = hullLabelsG
        .selectAll<SVGTextElement, { name: string; cx: number; cy: number; count: number }>("text")
        .data(hullData, (d) => d.name)
      labelSel.exit().remove()
      const labelEnter = labelSel
        .enter()
        .append("text")
        .attr("text-anchor", "middle")
        .attr("font-size", 12)
        .attr("font-weight", 600)
        .attr("fill", (d) => moduleColor.get(d.name) || "#374151")
        .attr("pointer-events", "none")
      labelEnter
        .merge(labelSel)
        .attr("x", (d) => d.cx)
        .attr("y", (d) => d.cy - 6)
        .text((d) => `${d.name} (${d.count})`)
    }

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

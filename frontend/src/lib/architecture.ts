export interface ArchNode {
  path: string
  label: string
  module: string
  layer: number
  language: string
  coupling: number
  fan_in: number
  fan_out: number
  external_fan_out: number
  category: string
}

export interface ArchEdge {
  from: string
  to: string
}

export interface ArchModule {
  name: string
  color: string
  node_count: number
}

export interface ModuleFlow {
  from: string
  to: string
  count: number
}

export interface ArchitectureView {
  schema_version: number
  nodes: ArchNode[]
  edges: ArchEdge[]
  modules: ArchModule[]
  module_flows: ModuleFlow[]
  layer_count: number
  stats: {
    node_count: number
    edge_count: number
    module_count: number
    is_dag: boolean
    largest_scc: number
  }
}

export const HOTSPOT_CATEGORY_COLOR: Record<string, string> = {
  hotspot: "#dc2626",
  active_stable: "#f59e0b",
  neglected_complex: "#eab308",
  stable: "#9ca3af",
}

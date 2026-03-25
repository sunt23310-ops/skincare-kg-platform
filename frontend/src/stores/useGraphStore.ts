// ============================================================
// Graph Store - Manages G6 graph data, layout, and selection
// ============================================================

import { defineStore, storeToRefs } from 'pinia'
import { ref, watch } from 'vue'
import type { G6GraphData, G6NodeData, G6EdgeData } from '@/types'
import { REL_TYPE_MAP } from '@/utils/constants'
import { useFilterStore } from './useFilterStore'

// Static JSON will be imported at build time.
// The actual files don't exist yet; the imports are typed so the
// rest of the code compiles once the data is available.
let rawNodes: G6NodeData[] = []
let rawEdges: G6EdgeData[] = []

try {
  // Dynamic imports wrapped in try/catch so the app doesn't crash
  // if the data files haven't been created yet.
  const nodesModule = import.meta.glob('@/data/nodes.json', { eager: true })
  const edgesModule = import.meta.glob('@/data/edges.json', { eager: true })

  const nodesEntry = Object.values(nodesModule)[0] as any
  const edgesEntry = Object.values(edgesModule)[0] as any

  if (nodesEntry) rawNodes = (nodesEntry.default ?? nodesEntry) as G6NodeData[]
  if (edgesEntry) rawEdges = (edgesEntry.default ?? edgesEntry) as G6EdgeData[]
} catch {
  // data files not present yet – work with empty arrays
}

export type LayoutType = 'force' | 'concentric' | 'tree'

const NODE_LIMIT = 300

// Pre-compute node degrees from raw edges for layered loading
function getNodeDegrees(edges: G6EdgeData[]): Map<string, number> {
  const degrees = new Map<string, number>()
  for (const e of edges) {
    degrees.set(e.source, (degrees.get(e.source) || 0) + 1)
    degrees.set(e.target, (degrees.get(e.target) || 0) + 1)
  }
  return degrees
}

// Pre-compute intra-layer degrees (only edges where both endpoints share the same layer)
function getIntraLayerDegrees(nodes: G6NodeData[], edges: G6EdgeData[]): Map<string, number> {
  const nodeLayer = new Map<string, string>()
  for (const n of nodes) nodeLayer.set(n.id, n.data.layer)
  const degrees = new Map<string, number>()
  for (const e of edges) {
    if (nodeLayer.get(e.source) === nodeLayer.get(e.target)) {
      degrees.set(e.source, (degrees.get(e.source) || 0) + 1)
      degrees.set(e.target, (degrees.get(e.target) || 0) + 1)
    }
  }
  return degrees
}

export const useGraphStore = defineStore('graph', () => {
  // ----- State -----
  const graphData = ref<G6GraphData | null>(null)
  const loading = ref(false)
  const layoutType = ref<LayoutType>('force')
  const selectedNodeId = ref<string | null>(null)
  const expandedNodeId = ref<string | null>(null)
  const clusterMode = ref(false)
  const totalFilteredCount = ref(0) // count before NODE_LIMIT truncation

  // ----- Filter store dependency -----
  const filterStore = useFilterStore()
  const { activeFilters } = storeToRefs(filterStore)

  // ----- Internal helpers -----

  const nodeDegrees = getNodeDegrees(rawEdges)
  const intraLayerDegrees = getIntraLayerDegrees(rawNodes, rawEdges)

  function filterNodes(nodes: G6NodeData[]): G6NodeData[] {
    const f = activeFilters.value
    const hasSearch = !!f.search
    const hasEntityTypeFilter = f.entityTypes && f.entityTypes.length > 0

    let filtered = nodes.filter((node) => {
      // Layer filter
      if (f.layer && node.data.layer !== f.layer) return false
      // Entity type filter
      if (f.entityTypes && f.entityTypes.length > 0) {
        if (!f.entityTypes.includes(node.data.entityType)) return false
      }
      // Search filter
      if (f.search) {
        const q = f.search.toLowerCase()
        const labelMatch = node.data.label.toLowerCase().includes(q)
        const labelEnMatch = node.data.labelEn?.toLowerCase().includes(q) ?? false
        if (!labelMatch && !labelEnMatch) return false
      }

      // Layered loading rules (skip when user is searching)
      if (!hasSearch) {
        // Rule 1: L5 nodes hidden by default (unless entityType filter is active)
        if (node.data.layer === 'L5' && !hasEntityTypeFilter) return false
        // Rule 2: For L2, only show nodes with intra-layer edges (114 vs 1134)
        if (node.data.layer === 'L2' && (intraLayerDegrees.get(node.id) || 0) === 0) return false
      }

      return true
    })

    // Track count before truncation
    totalFilteredCount.value = filtered.length

    // Rule 3: Truncate to NODE_LIMIT by degree (skip when searching)
    if (filtered.length > NODE_LIMIT && !hasSearch) {
      filtered.sort((a, b) => (nodeDegrees.get(b.id) || 0) - (nodeDegrees.get(a.id) || 0))
      filtered = filtered.slice(0, NODE_LIMIT)
    }

    return filtered
  }

  function filterEdges(edges: G6EdgeData[], nodeIds: Set<string>): G6EdgeData[] {
    const f = activeFilters.value
    return edges.filter((edge) => {
      // Both endpoints must be in the visible node set
      if (!nodeIds.has(edge.source) || !nodeIds.has(edge.target)) return false
      // Rel category filter
      if (f.relCategories && f.relCategories.length > 0) {
        if (!f.relCategories.includes(edge.data.category)) return false
      }
      return true
    })
  }

  // ----- Actions -----

  function loadGraphData() {
    loading.value = true
    try {
      const nodes = filterNodes(rawNodes)
      const nodeIdSet = new Set(nodes.map((n) => n.id))
      const edges = filterEdges(rawEdges, nodeIdSet)
      graphData.value = { nodes, edges }
    } finally {
      loading.value = false
    }
  }

  /**
   * Expand a node by finding its 2-hop neighbors and adding them
   * to the current graph data.
   */
  function expandNode(nodeId: string) {
    expandedNodeId.value = nodeId
    if (!graphData.value) {
      loadGraphData()
      return
    }

    const existingIds = new Set(graphData.value.nodes.map((n) => n.id))

    // 1-hop neighbors
    const hop1Edges = rawEdges.filter(
      (e) => e.source === nodeId || e.target === nodeId
    )
    const hop1Ids = new Set<string>()
    for (const e of hop1Edges) {
      hop1Ids.add(e.source)
      hop1Ids.add(e.target)
    }

    // 2-hop neighbors
    const hop2Edges = rawEdges.filter(
      (e) => hop1Ids.has(e.source) || hop1Ids.has(e.target)
    )
    const hop2Ids = new Set<string>()
    for (const e of hop2Edges) {
      hop2Ids.add(e.source)
      hop2Ids.add(e.target)
    }

    // Collect new nodes
    const allTargetIds = new Set([...hop1Ids, ...hop2Ids])
    const newNodes = rawNodes.filter(
      (n) => allTargetIds.has(n.id) && !existingIds.has(n.id)
    )

    // Collect new edges (both endpoints must be in the combined set)
    const combinedIds = new Set([...existingIds, ...allTargetIds])
    const relevantEdges = rawEdges.filter(
      (e) => combinedIds.has(e.source) && combinedIds.has(e.target)
    )
    const existingEdgeIds = new Set(graphData.value.edges.map((e) => e.id))
    const newEdges = relevantEdges.filter((e) => !existingEdgeIds.has(e.id))

    graphData.value = {
      nodes: [...graphData.value.nodes, ...newNodes],
      edges: [...graphData.value.edges, ...newEdges],
    }
  }

  function setLayout(type: LayoutType) {
    layoutType.value = type
  }

  function selectNode(nodeId: string | null) {
    selectedNodeId.value = nodeId
  }

  function toggleClusterMode() {
    clusterMode.value = !clusterMode.value
  }

  // ----- Auto-reload when filters change -----
  watch(activeFilters, () => {
    loadGraphData()
  }, { deep: true })

  // Initial load
  loadGraphData()

  // Expose all raw data for drawer/matrix lookups
  const allNodes = rawNodes
  const allEdges = rawEdges

  function collapseExpansion() {
    expandedNodeId.value = null
    loadGraphData()
  }

  return {
    // state
    graphData,
    loading,
    layoutType,
    selectedNodeId,
    expandedNodeId,
    clusterMode,
    totalFilteredCount,
    allNodes,
    allEdges,
    // actions
    loadGraphData,
    expandNode,
    collapseExpansion,
    setLayout,
    selectNode,
    toggleClusterMode,
  }
})

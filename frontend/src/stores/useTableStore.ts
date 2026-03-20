// ============================================================
// Table Store - Manages table data with pagination
// ============================================================

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { LayerCode, G6NodeData } from '@/types'
import { LAYER_TABS } from '@/utils/constants'

// Static JSON data – same approach as graph store
let rawNodes: G6NodeData[] = []

try {
  const nodesModule = import.meta.glob('@/data/nodes.json', { eager: true })
  const nodesEntry = Object.values(nodesModule)[0] as any
  if (nodesEntry) rawNodes = (nodesEntry.default ?? nodesEntry) as G6NodeData[]
} catch {
  // data files not present yet
}

export const useTableStore = defineStore('table', () => {
  // ----- State -----
  const activeLayerTab = ref<LayerCode>('L0')
  const activeSubTab = ref<string>('')
  const tableData = ref<Record<string, any>[]>([])
  const loading = ref(false)
  const page = ref(1)
  const pageSize = ref(20)
  const total = ref(0)
  const selectedRowId = ref<string | null>(null)

  // ----- Derived -----

  /** Current layer tab definition */
  const currentLayerDef = computed(() =>
    LAYER_TABS.find((t) => t.layer === activeLayerTab.value)
  )

  /** Current sub-tab definition */
  const currentSubTabDef = computed(() =>
    currentLayerDef.value?.subTabs.find((s) => s.key === activeSubTab.value)
  )

  // ----- Actions -----

  function setLayerTab(layer: LayerCode) {
    activeLayerTab.value = layer
    // Auto-select first sub-tab
    const layerDef = LAYER_TABS.find((t) => t.layer === layer)
    if (layerDef && layerDef.subTabs.length > 0) {
      activeSubTab.value = layerDef.subTabs[0].key
    }
    page.value = 1
    fetchTableData()
  }

  function setSubTab(subTabKey: string) {
    activeSubTab.value = subTabKey
    page.value = 1
    fetchTableData()
  }

  /**
   * Filter static JSON data by entity type (from current sub-tab)
   * and apply pagination.
   */
  function fetchTableData() {
    const subTab = currentSubTabDef.value
    if (!subTab) {
      tableData.value = []
      total.value = 0
      return
    }

    // Filter nodes by entity type
    const filtered = rawNodes.filter(
      (n) => n.data.entityType === subTab.entityType
    )

    // Map to flat row objects for the table
    const rows = filtered.map((n) => ({
      id: n.id,
      label: n.data.label,
      labelEn: n.data.labelEn ?? '',
      layer: n.data.layer,
      entityType: n.data.entityType,
      ...n.data.properties,
    }))

    total.value = rows.length

    // Paginate
    const start = (page.value - 1) * pageSize.value
    const end = start + pageSize.value
    tableData.value = rows.slice(start, end)
  }

  function selectRow(rowId: string | null) {
    selectedRowId.value = rowId
  }

  function setPage(p: number) {
    page.value = p
    fetchTableData()
  }

  function setPageSize(size: number) {
    pageSize.value = size
    page.value = 1
    fetchTableData()
  }

  // Initialize with first layer & sub-tab
  const firstLayer = LAYER_TABS[0]
  if (firstLayer) {
    activeLayerTab.value = firstLayer.layer
    if (firstLayer.subTabs.length > 0) {
      activeSubTab.value = firstLayer.subTabs[0].key
    }
  }

  return {
    // state
    activeLayerTab,
    activeSubTab,
    tableData,
    loading,
    page,
    pageSize,
    total,
    selectedRowId,
    // computed
    currentLayerDef,
    currentSubTabDef,
    // actions
    setLayerTab,
    setSubTab,
    fetchTableData,
    selectRow,
    setPage,
    setPageSize,
  }
})

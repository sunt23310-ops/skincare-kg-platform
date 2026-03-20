// ============================================================
// Selection Store - Cross-component entity selection state
// ============================================================

import { defineStore } from 'pinia'
import { ref } from 'vue'

export type SelectionSource = 'graph' | 'table' | 'toolbar' | null

export const useSelectionStore = defineStore('selection', () => {
  // ----- State -----
  const entityId = ref<string | null>(null)
  const source = ref<SelectionSource>(null)
  const hoveredEntityId = ref<string | null>(null)

  // ----- Actions -----

  function select(id: string | null, src: SelectionSource = null) {
    entityId.value = id
    source.value = src
  }

  function clearSelection() {
    entityId.value = null
    source.value = null
  }

  function setHovered(id: string | null) {
    hoveredEntityId.value = id
  }

  return {
    // state
    entityId,
    source,
    hoveredEntityId,
    // actions
    select,
    clearSelection,
    setHovered,
  }
})

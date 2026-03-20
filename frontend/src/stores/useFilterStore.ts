// ============================================================
// Filter Store - Controls graph & table filtering
// ============================================================

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { LayerCode, RelCategory, GraphQueryParams } from '@/types'
import { ALL_REL_CATEGORIES } from '@/utils/constants'

export const useFilterStore = defineStore('filter', () => {
  // ----- State -----
  const layer = ref<LayerCode | undefined>(undefined)
  const entityTypes = ref<string[]>([])
  const searchQuery = ref('')
  const relCategories = ref<RelCategory[]>([...ALL_REL_CATEGORIES])

  // ----- Getters -----
  const activeFilters = computed<GraphQueryParams>(() => ({
    layer: layer.value,
    entityTypes: entityTypes.value.length > 0 ? entityTypes.value : undefined,
    search: searchQuery.value || undefined,
    relCategories:
      relCategories.value.length < ALL_REL_CATEGORIES.length
        ? relCategories.value
        : undefined,
  }))

  // ----- Actions -----
  function setLayer(newLayer: LayerCode | undefined) {
    layer.value = newLayer
  }

  function toggleEntityType(entityType: string) {
    const idx = entityTypes.value.indexOf(entityType)
    if (idx === -1) {
      entityTypes.value.push(entityType)
    } else {
      entityTypes.value.splice(idx, 1)
    }
  }

  function setSearch(query: string) {
    searchQuery.value = query
  }

  function toggleRelCategory(category: RelCategory) {
    const idx = relCategories.value.indexOf(category)
    if (idx === -1) {
      relCategories.value.push(category)
    } else {
      relCategories.value.splice(idx, 1)
    }
  }

  function resetFilters() {
    layer.value = undefined
    entityTypes.value = []
    searchQuery.value = ''
    relCategories.value = [...ALL_REL_CATEGORIES]
  }

  return {
    // state
    layer,
    entityTypes,
    searchQuery,
    relCategories,
    // getters
    activeFilters,
    // actions
    setLayer,
    toggleEntityType,
    setSearch,
    toggleRelCategory,
    resetFilters,
  }
})

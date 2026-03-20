// ============================================================
// Drawer Store - Entity detail drawer state
// ============================================================

import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { LayerCode } from '@/types'

export type DrawerTab = 'properties' | 'relationships' | 'history'

export const useDrawerStore = defineStore('drawer', () => {
  // ----- State -----
  const visible = ref(false)
  const entityId = ref<string | null>(null)
  const entityLayer = ref<LayerCode | null>(null)
  const entityType = ref<string | null>(null)
  const activeTab = ref<DrawerTab>('properties')

  // ----- Actions -----

  function open(id: string, layer?: LayerCode, type?: string) {
    entityId.value = id
    entityLayer.value = layer ?? null
    entityType.value = type ?? null
    activeTab.value = 'properties'
    visible.value = true
  }

  function close() {
    visible.value = false
    // Keep entity data briefly so closing animation can reference it
    setTimeout(() => {
      if (!visible.value) {
        entityId.value = null
        entityLayer.value = null
        entityType.value = null
        activeTab.value = 'properties'
      }
    }, 300)
  }

  function setTab(tab: DrawerTab) {
    activeTab.value = tab
  }

  return {
    // state
    visible,
    entityId,
    entityLayer,
    entityType,
    activeTab,
    // actions
    open,
    close,
    setTab,
  }
})

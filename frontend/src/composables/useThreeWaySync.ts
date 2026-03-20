import { watch } from 'vue'
import { useFilterStore } from '@/stores/useFilterStore'
import { useGraphStore } from '@/stores/useGraphStore'
import { useTableStore } from '@/stores/useTableStore'
import { useSelectionStore } from '@/stores/useSelectionStore'
import { useDrawerStore } from '@/stores/useDrawerStore'

/**
 * Three-way synchronization between Toolbar, Graph, and Table.
 * Uses source-guard pattern to prevent circular updates.
 */
export function useThreeWaySync() {
  const filterStore = useFilterStore()
  const graphStore = useGraphStore()
  const tableStore = useTableStore()
  const selectionStore = useSelectionStore()
  const drawerStore = useDrawerStore()

  // 1. Filter change → refresh both graph and table
  watch(
    () => ({
      layer: filterStore.layer,
      entityTypes: filterStore.entityTypes,
      search: filterStore.searchQuery,
      relCategories: [...filterStore.relCategories],
    }),
    () => {
      graphStore.loadGraphData()
      tableStore.fetchTableData()
    },
    { deep: true }
  )

  // 2. Selection sync with source guard
  watch(
    () => selectionStore.entityId,
    (id) => {
      if (!id) {
        drawerStore.close()
        return
      }

      // Open drawer on any selection
      const node = graphStore.allNodes?.find((n: any) => n.id === id)
      if (node) {
        drawerStore.open(id)
      }

      // Sync table highlight if selection came from graph
      if (selectionStore.source === 'graph') {
        tableStore.selectedRowId = id
      }
    }
  )

  // 3. Layer tab change in table syncs toolbar
  watch(
    () => tableStore.activeLayerTab,
    (layer) => {
      if (layer && filterStore.layer !== layer) {
        filterStore.setLayer(layer)
      }
    }
  )
}

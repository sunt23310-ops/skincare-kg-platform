<template>
  <div class="data-table-panel">
    <!-- Layer Tab Bar -->
    <div class="layer-tabs">
      <div
        v-for="(group, gi) in tabGroups"
        :key="gi"
        class="tab-group"
      >
        <span v-if="gi > 0" class="tab-separator">·</span>
        <div
          v-for="tab in group.tabs"
          :key="tab.layer"
          class="layer-tab"
          :class="{ active: filterStore.layer === tab.layer }"
          @click="filterStore.setLayer(tab.layer)"
        >
          {{ tab.label }}
        </div>
      </div>
    </div>

    <!-- Sub-tabs -->
    <el-tabs v-model="activeSubTab" class="sub-tabs" @tab-change="onSubTabChange">
      <el-tab-pane
        v-for="sub in currentSubTabs"
        :key="sub.key"
        :label="sub.label"
        :name="sub.key"
      />
    </el-tabs>

    <!-- Table -->
    <div class="table-wrapper">
      <el-table
        :data="tableStore.tableData"
        :height="tableHeight"
        stripe
        highlight-current-row
        :current-row-key="selectionStore.entityId"
        row-key="id"
        size="default"
        @row-click="onRowClick"
        @row-dblclick="onRowDblClick"
        v-loading="tableStore.loading"
      >
        <el-table-column type="index" width="50" label="#" />
        <el-table-column
          v-for="col in currentColumns"
          :key="col.prop"
          :prop="col.prop"
          :label="col.label"
          :width="col.width"
          :sortable="col.sortable"
          show-overflow-tooltip
        >
          <template #default="{ row }">
            <template v-if="col.type === 'tag'">
              <el-tag
                v-for="t in (Array.isArray(row[col.prop]) ? row[col.prop] : [row[col.prop]]).filter(Boolean)"
                :key="t"
                size="small"
                class="cell-tag"
              >
                {{ t }}
              </el-tag>
            </template>
            <template v-else-if="col.type === 'status'">
              <el-tag
                :type="row[col.prop] === 'safe' ? 'success' : row[col.prop] === 'caution' ? 'danger' : 'warning'"
                size="small"
              >
                {{ row[col.prop] }}
              </el-tag>
            </template>
            <template v-else>
              {{ col.formatter ? col.formatter(row) : row[col.prop] }}
            </template>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click.stop="onViewDetail(row)">
              详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- Pagination -->
      <div class="table-pagination">
        <el-pagination
          v-model:current-page="tableStore.page"
          v-model:page-size="tableStore.pageSize"
          :total="tableStore.total"
          :page-sizes="[20, 50, 100]"
          layout="total, sizes, prev, pager, next"
          small
          @size-change="tableStore.fetchTableData()"
          @current-change="tableStore.fetchTableData()"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useFilterStore } from '@/stores/useFilterStore'
import { useTableStore } from '@/stores/useTableStore'
import { useSelectionStore } from '@/stores/useSelectionStore'
import { useDrawerStore } from '@/stores/useDrawerStore'
import { LAYER_TABS } from '@/utils/constants'
import type { LayerCode, TableColumnDef } from '@/types'

const filterStore = useFilterStore()
const tableStore = useTableStore()
const selectionStore = useSelectionStore()
const drawerStore = useDrawerStore()

const tableHeight = ref(500)
const activeSubTab = ref('')

const tabGroups = [
  {
    label: '基础层',
    tabs: [
      { layer: 'L0' as LayerCode, label: 'L0 画像配置' },
      { layer: 'L1' as LayerCode, label: 'L1 商品' },
    ],
  },
  {
    label: '知识层',
    tabs: [
      { layer: 'L2' as LayerCode, label: 'L2 知识' },
      { layer: 'L3' as LayerCode, label: 'L3 方案' },
    ],
  },
  {
    label: '引擎层',
    tabs: [
      { layer: 'L4' as LayerCode, label: 'L4 对话' },
      { layer: 'L5' as LayerCode, label: 'L5 词汇' },
    ],
  },
]

const currentLayerTab = computed(() => {
  return LAYER_TABS.find(t => t.layer === filterStore.layer)
})

const currentSubTabs = computed(() => {
  return currentLayerTab.value?.subTabs || []
})

const currentColumns = computed<TableColumnDef[]>(() => {
  const sub = currentSubTabs.value.find(s => s.key === activeSubTab.value)
  return sub?.columns || []
})

// Sync activeSubTab when layer changes
watch(
  () => filterStore.layer,
  () => {
    const subs = currentSubTabs.value
    if (subs.length > 0) {
      activeSubTab.value = subs[0].key
    }
    tableStore.fetchTableData()
  },
  { immediate: true }
)

function onSubTabChange(tab: string) {
  tableStore.activeSubTab = tab
  tableStore.fetchTableData()
}

function onRowClick(row: any) {
  selectionStore.select(row.id, 'table')
}

function onRowDblClick(row: any) {
  selectionStore.select(row.id, 'table')
  drawerStore.open(row.id)
}

function onViewDetail(row: any) {
  selectionStore.select(row.id, 'table')
  drawerStore.open(row.id)
}

onMounted(() => {
  // Calculate available height
  const el = document.querySelector('.table-wrapper')
  if (el) {
    tableHeight.value = el.clientHeight - 50
  }
})
</script>

<style scoped lang="scss">
.data-table-panel {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #FFFFFF;
}

.layer-tabs {
  display: flex;
  align-items: center;
  padding: 0 12px;
  border-bottom: 1px solid #E2E8F0;
  height: 40px;
  gap: 0;
  flex-shrink: 0;
}

.tab-group {
  display: flex;
  align-items: center;
}

.tab-separator {
  color: #CBD5E1;
  padding: 0 8px;
  font-size: 18px;
}

.layer-tab {
  padding: 8px 14px;
  font-size: 13px;
  color: #64748B;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: all 0.2s;
  white-space: nowrap;

  &:hover {
    color: #3B82F6;
  }

  &.active {
    color: #3B82F6;
    font-weight: 600;
    border-bottom-color: #3B82F6;
  }
}

.sub-tabs {
  flex-shrink: 0;
  :deep(.el-tabs__header) {
    margin: 0;
    padding: 0 12px;
  }
  :deep(.el-tabs__item) {
    font-size: 13px;
    height: 36px;
  }
}

.table-wrapper {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.cell-tag {
  margin-right: 4px;
  margin-bottom: 2px;
}

.table-pagination {
  padding: 8px 12px;
  border-top: 1px solid #E2E8F0;
  display: flex;
  justify-content: flex-end;
  flex-shrink: 0;
}
</style>

<template>
  <el-dialog
    v-model="visible"
    title="成分关系矩阵"
    fullscreen
    :close-on-click-modal="false"
  >
    <div class="matrix-container">
      <div class="matrix-toolbar">
        <el-input
          v-model="searchText"
          placeholder="搜索成分..."
          :prefix-icon="Search"
          clearable
          style="width: 200px"
        />
        <div class="matrix-legend">
          <span class="legend-item"><span class="dot" style="background: #EF4444" /> 冲突</span>
          <span class="legend-item"><span class="dot" style="background: #22C55E" /> 协同</span>
          <span class="legend-item"><span class="dot" style="background: #F59E0B" /> 风险/耐受</span>
          <span class="legend-item"><span class="dot" style="background: #CBD5E1" /> 无关系</span>
        </div>
      </div>

      <div class="matrix-scroll">
        <table class="matrix-table">
          <thead>
            <tr>
              <th class="corner-cell">成分</th>
              <th
                v-for="col in filteredIngredients"
                :key="col.id"
                class="header-cell"
                :title="col.data.label"
              >
                <span class="rotated-text">{{ col.data.label }}</span>
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in filteredIngredients" :key="row.id">
              <td class="row-header">{{ row.data.label }}</td>
              <td
                v-for="col in filteredIngredients"
                :key="col.id"
                class="matrix-cell"
                :class="getCellClass(row.id, col.id)"
                @click="onCellClick(row, col)"
              >
                <span v-if="row.id !== col.id" class="cell-dot" :style="getCellStyle(row.id, col.id)" />
                <span v-else class="cell-diagonal" />
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Cell detail popover -->
    <el-dialog
      v-model="cellDialogVisible"
      :title="cellDialogTitle"
      width="400px"
      append-to-body
    >
      <el-form v-if="selectedCell" label-width="80px" size="small">
        <el-form-item label="关系类型">
          <el-select v-model="selectedCell.relType">
            <el-option label="冲突 (conflicts_with)" value="conflicts_with" />
            <el-option label="协同 (synergizes_with)" value="synergizes_with" />
            <el-option label="风险 (risk_for)" value="risk_for" />
            <el-option label="耐受 (requires_tolerance)" value="requires_tolerance" />
            <el-option label="无关系" value="" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="selectedCell.relType === 'conflicts_with'" label="冲突类型">
          <el-select v-model="selectedCell.constraintType">
            <el-option label="不可同时使用" value="不可同时使用" />
            <el-option label="需间隔使用" value="需间隔使用" />
            <el-option label="降低效果" value="降低效果" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="selectedCell.constraintType === '需间隔使用'" label="间隔时间">
          <el-input v-model="selectedCell.interval" placeholder="如 12h+" />
        </el-form-item>
        <el-form-item label="说明">
          <el-input v-model="selectedCell.note" type="textarea" :rows="3" placeholder="解释说明（必填）" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="cellDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveCellRelation">保存</el-button>
      </template>
    </el-dialog>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, inject } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { useGraphStore } from '@/stores/useGraphStore'

const visible = defineModel<boolean>({ default: false })
const graphStore = useGraphStore()
const searchText = ref('')

const ingredients = computed(() => {
  return (graphStore.allNodes || []).filter((n: any) => n.data?.entityType === 'Ingredient')
})

const filteredIngredients = computed(() => {
  if (!searchText.value) return ingredients.value
  const q = searchText.value.toLowerCase()
  return ingredients.value.filter((n: any) =>
    n.data?.label?.toLowerCase().includes(q) ||
    n.data?.properties?.code?.toLowerCase().includes(q)
  )
})

// Build a relation map for O(1) lookup
const relationMap = computed(() => {
  const map: Record<string, any> = {}
  for (const edge of (graphStore.allEdges || [])) {
    const key1 = `${edge.source}__${edge.target}`
    const key2 = `${edge.target}__${edge.source}`
    map[key1] = edge
    if (['conflicts_with', 'synergizes_with'].includes(edge.data?.relType)) {
      map[key2] = edge
    }
  }
  return map
})

function getCellStyle(rowId: string, colId: string) {
  const rel = relationMap.value[`${rowId}__${colId}`]
  if (!rel) return { background: '#E2E8F0', width: '10px', height: '10px', borderRadius: '50%', display: 'inline-block' }
  const colors: Record<string, string> = {
    conflicts_with: '#EF4444',
    synergizes_with: '#22C55E',
    risk_for: '#F59E0B',
    requires_tolerance: '#F59E0B',
  }
  return {
    background: colors[rel.data?.relType] || '#94A3B8',
    width: '12px',
    height: '12px',
    borderRadius: '50%',
    display: 'inline-block',
  }
}

function getCellClass(rowId: string, colId: string) {
  const rel = relationMap.value[`${rowId}__${colId}`]
  return rel ? 'has-relation' : ''
}

// Cell dialog
const cellDialogVisible = ref(false)
const cellDialogTitle = ref('')
const selectedCell = ref<any>(null)

function onCellClick(row: any, col: any) {
  if (row.id === col.id) return
  const rel = relationMap.value[`${row.id}__${col.id}`]
  cellDialogTitle.value = `${row.data.label} ↔ ${col.data.label}`
  selectedCell.value = {
    sourceId: row.id,
    targetId: col.id,
    relType: rel?.data?.relType || '',
    constraintType: rel?.data?.properties?.constraint_type || '',
    interval: rel?.data?.properties?.interval || '',
    note: rel?.data?.properties?.note || '',
  }
  cellDialogVisible.value = true
}

function saveCellRelation() {
  // In a real app, this would call the API
  cellDialogVisible.value = false
}
</script>

<style scoped lang="scss">
.matrix-container {
  height: calc(100vh - 120px);
  display: flex;
  flex-direction: column;
}

.matrix-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 0;
  margin-bottom: 8px;
}

.matrix-legend {
  display: flex;
  gap: 16px;
  font-size: 13px;
  color: #64748B;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  display: inline-block;
}

.matrix-scroll {
  flex: 1;
  overflow: auto;
}

.matrix-table {
  border-collapse: collapse;
  font-size: 12px;

  th, td {
    border: 1px solid #E2E8F0;
    text-align: center;
    padding: 0;
  }

  .corner-cell {
    width: 100px;
    min-width: 100px;
    background: #F8FAFC;
    position: sticky;
    left: 0;
    top: 0;
    z-index: 3;
  }

  .header-cell {
    width: 40px;
    min-width: 40px;
    height: 100px;
    background: #F8FAFC;
    position: sticky;
    top: 0;
    z-index: 2;
  }

  .rotated-text {
    display: block;
    transform: rotate(-60deg);
    white-space: nowrap;
    font-size: 11px;
    transform-origin: center center;
  }

  .row-header {
    width: 100px;
    min-width: 100px;
    text-align: right;
    padding: 4px 8px;
    background: #F8FAFC;
    position: sticky;
    left: 0;
    z-index: 1;
    font-weight: 500;
  }

  .matrix-cell {
    width: 40px;
    min-width: 40px;
    height: 32px;
    cursor: pointer;

    &:hover {
      background: #F1F5F9;
    }

    &.has-relation:hover {
      background: #EFF6FF;
    }
  }

  .cell-dot {
    cursor: pointer;
  }

  .cell-diagonal {
    display: block;
    width: 100%;
    height: 100%;
    background: repeating-linear-gradient(
      45deg,
      transparent,
      transparent 3px,
      #F1F5F9 3px,
      #F1F5F9 6px
    );
  }
}
</style>

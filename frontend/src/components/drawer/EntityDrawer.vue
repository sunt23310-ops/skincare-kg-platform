<template>
  <el-drawer
    v-model="drawerStore.visible"
    :title="entityLabel"
    direction="rtl"
    size="420px"
    :destroy-on-close="false"
  >
    <template #header>
      <div class="drawer-header">
        <div class="header-info">
          <el-tag :color="entityColor" effect="dark" size="small">{{ entityType }}</el-tag>
          <el-tag type="info" size="small">{{ entityLayer }}</el-tag>
          <h4>{{ entityLabel }}</h4>
        </div>
      </div>
    </template>

    <el-tabs v-model="drawerStore.activeTab" class="drawer-tabs">
      <!-- Properties Tab -->
      <el-tab-pane label="属性" name="properties">
        <div class="properties-tab">
          <el-descriptions :column="1" border size="small">
            <el-descriptions-item
              v-for="(value, key) in entityProperties"
              :key="key"
              :label="String(key)"
            >
              <template v-if="Array.isArray(value)">
                <el-tag
                  v-for="v in value"
                  :key="v"
                  size="small"
                  style="margin: 2px"
                >
                  {{ v }}
                </el-tag>
              </template>
              <template v-else-if="key === 'riskLevel'">
                <el-tag
                  :type="value === 'safe' ? 'success' : value === 'caution' ? 'danger' : 'warning'"
                  size="small"
                >
                  {{ value }}
                </el-tag>
              </template>
              <template v-else>
                {{ value }}
              </template>
            </el-descriptions-item>
          </el-descriptions>
        </div>
      </el-tab-pane>

      <!-- Relationships Tab -->
      <el-tab-pane label="关系" name="relationships">
        <div class="relationships-tab">
          <div v-if="entityRelationships.length === 0" class="empty-state">
            <el-empty description="暂无关联关系" :image-size="80" />
          </div>
          <div v-else>
            <div
              v-for="(group, category) in groupedRelationships"
              :key="category"
              class="rel-group"
            >
              <div class="rel-group-header">
                <el-tag
                  :style="{ background: getCategoryColor(String(category)) + '20', color: getCategoryColor(String(category)), borderColor: getCategoryColor(String(category)) }"
                  size="small"
                >
                  {{ category }}
                </el-tag>
                <span class="rel-count">{{ group.length }}条</span>
              </div>
              <div
                v-for="rel in group"
                :key="rel.id"
                class="rel-item"
                @click="onRelClick(rel)"
              >
                <span class="rel-label">{{ rel.data.label }}</span>
                <span class="rel-arrow">→</span>
                <span class="rel-target">{{ getTargetLabel(rel) }}</span>
                <el-tag v-if="rel.data.properties?.constraint_type" size="small" type="warning" class="rel-meta">
                  {{ rel.data.properties.constraint_type }}
                </el-tag>
              </div>
            </div>
          </div>
        </div>
      </el-tab-pane>

      <!-- History Tab -->
      <el-tab-pane label="历史" name="history">
        <div class="history-tab">
          <el-timeline>
            <el-timeline-item
              v-for="(item, i) in mockHistory"
              :key="i"
              :timestamp="item.time"
              :type="item.type"
              placement="top"
            >
              <div class="history-item">
                <span class="history-user">{{ item.user }}</span>
                <span class="history-action">{{ item.action }}</span>
              </div>
            </el-timeline-item>
          </el-timeline>
        </div>
      </el-tab-pane>
    </el-tabs>
  </el-drawer>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useDrawerStore } from '@/stores/useDrawerStore'
import { useGraphStore } from '@/stores/useGraphStore'
import { useSelectionStore } from '@/stores/useSelectionStore'
import { REL_TYPE_TO_CATEGORY, getNodeStyle } from '@/components/graph/config/nodeStyles'
import type { G6EdgeData, RelCategory } from '@/types'

const drawerStore = useDrawerStore()
const graphStore = useGraphStore()
const selectionStore = useSelectionStore()

const currentNode = computed(() => {
  if (!drawerStore.entityId || !graphStore.allNodes) return null
  return graphStore.allNodes.find((n: any) => n.id === drawerStore.entityId)
})

const entityLabel = computed(() => currentNode.value?.data?.label || '')
const entityType = computed(() => currentNode.value?.data?.entityType || '')
const entityLayer = computed(() => currentNode.value?.data?.layer || '')
const entityColor = computed(() => {
  if (!currentNode.value) return '#3B82F6'
  return getNodeStyle(currentNode.value).fill as string
})
const entityProperties = computed(() => currentNode.value?.data?.properties || {})

const entityRelationships = computed<G6EdgeData[]>(() => {
  if (!drawerStore.entityId || !graphStore.allEdges) return []
  return graphStore.allEdges.filter(
    (e: any) => e.source === drawerStore.entityId || e.target === drawerStore.entityId
  )
})

const groupedRelationships = computed(() => {
  const groups: Record<string, G6EdgeData[]> = {}
  for (const rel of entityRelationships.value) {
    const cat = rel.data?.category || '其他'
    if (!groups[cat]) groups[cat] = []
    groups[cat].push(rel)
  }
  return groups
})

const CATEGORY_COLORS: Record<string, string> = {
  '等价映射': '#94A3B8',
  '替代递进': '#06B6D4',
  '协同增强': '#22C55E',
  '互斥约束': '#EF4444',
  '因果归因': '#6366F1',
  '组成归属': '#94A3B8',
}

function getCategoryColor(cat: string): string {
  return CATEGORY_COLORS[cat] || '#94A3B8'
}

function getTargetLabel(rel: G6EdgeData): string {
  const targetId = rel.source === drawerStore.entityId ? rel.target : rel.source
  const node = graphStore.allNodes?.find((n: any) => n.id === targetId)
  return node?.data?.label || targetId
}

function onRelClick(rel: G6EdgeData) {
  const targetId = rel.source === drawerStore.entityId ? rel.target : rel.source
  selectionStore.select(targetId, 'table')
  drawerStore.open(targetId)
}

const mockHistory = [
  { time: '2026-03-20 14:30', user: '管理员', action: '创建了该实体', type: 'primary' as const },
  { time: '2026-03-20 15:10', user: '管理员', action: '添加了3条关系', type: 'success' as const },
  { time: '2026-03-20 16:00', user: '审核员', action: '审核通过', type: 'success' as const },
]
</script>

<style scoped lang="scss">
.drawer-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.header-info {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;

  h4 {
    font-size: 16px;
    font-weight: 600;
    margin-left: 4px;
  }
}

.drawer-tabs {
  :deep(.el-tabs__header) {
    margin-bottom: 12px;
  }
}

.properties-tab {
  :deep(.el-descriptions__label) {
    width: 100px;
    font-weight: 500;
  }
}

.relationships-tab {
  .rel-group {
    margin-bottom: 16px;
  }

  .rel-group-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 8px;
  }

  .rel-count {
    font-size: 12px;
    color: #94A3B8;
  }

  .rel-item {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 6px 8px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 13px;

    &:hover {
      background: #F8FAFC;
    }
  }

  .rel-label {
    color: #64748B;
    font-size: 12px;
  }

  .rel-arrow {
    color: #CBD5E1;
  }

  .rel-target {
    color: #3B82F6;
    font-weight: 500;
  }

  .rel-meta {
    margin-left: auto;
    font-size: 11px;
  }
}

.history-tab {
  padding: 8px 0;

  .history-item {
    font-size: 13px;
  }

  .history-user {
    font-weight: 500;
    margin-right: 4px;
  }

  .history-action {
    color: #64748B;
  }
}

.empty-state {
  padding: 40px 0;
}
</style>

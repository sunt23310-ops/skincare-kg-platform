<template>
  <div class="graph-canvas" ref="containerRef">
    <!-- Graph Toolbar -->
    <div class="graph-toolbar">
      <el-button-group size="small">
        <el-tooltip content="力导向布局">
          <el-button :type="layoutType === 'force' ? 'primary' : ''" @click="setLayout('force')">
            <el-icon><Connection /></el-icon>
          </el-button>
        </el-tooltip>
        <el-tooltip content="同心圆布局">
          <el-button :type="layoutType === 'concentric' ? 'primary' : ''" @click="setLayout('concentric')">
            <el-icon><Aim /></el-icon>
          </el-button>
        </el-tooltip>
        <el-tooltip content="树状布局">
          <el-button :type="layoutType === 'tree' ? 'primary' : ''" @click="setLayout('tree')">
            <el-icon><SetUp /></el-icon>
          </el-button>
        </el-tooltip>
      </el-button-group>

      <el-divider direction="vertical" />

      <el-button-group size="small">
        <el-button @click="zoomIn"><el-icon><ZoomIn /></el-icon></el-button>
        <el-button @click="zoomOut"><el-icon><ZoomOut /></el-icon></el-button>
        <el-tooltip content="适应画布">
          <el-button @click="fitView"><el-icon><FullScreen /></el-icon></el-button>
        </el-tooltip>
      </el-button-group>

      <el-divider direction="vertical" />

      <el-tag type="info" size="small" class="node-count">
        {{ nodeCount }} 节点 · {{ edgeCount }} 关系
      </el-tag>
    </div>

    <!-- Loading overlay -->
    <div v-if="graphStore.loading" class="graph-loading">
      <el-icon class="is-loading" :size="32"><Loading /></el-icon>
      <span>加载图谱数据...</span>
    </div>

    <!-- Empty state -->
    <div v-if="!graphStore.loading && nodeCount === 0" class="graph-empty">
      <el-empty description="暂无图谱数据" :image-size="120" />
    </div>

    <!-- Breadcrumb for cross-layer expansion -->
    <div v-if="graphStore.expandedNodeId" class="graph-breadcrumb">
      <el-breadcrumb separator="/">
        <el-breadcrumb-item>
          <el-button link type="primary" size="small" @click="graphStore.collapseExpansion()">
            返回全图
          </el-button>
        </el-breadcrumb-item>
        <el-breadcrumb-item>{{ expandedLabel }} · 2跳邻域</el-breadcrumb-item>
      </el-breadcrumb>
    </div>

    <!-- Hint bar -->
    <div class="graph-hint">
      右键节点可编辑属性/添加关系 · 双击展开邻域 · 滚轮缩放
    </div>

    <!-- Context Menu -->
    <div
      v-if="contextMenu.visible"
      class="context-menu"
      :style="{ left: contextMenu.x + 'px', top: contextMenu.y + 'px' }"
    >
      <div class="menu-item" @click="onContextAction('detail')">
        <el-icon><View /></el-icon> 查看详情
      </div>
      <div class="menu-item" @click="onContextAction('edit')">
        <el-icon><Edit /></el-icon> 编辑属性
      </div>
      <div class="menu-item" @click="onContextAction('addRel')">
        <el-icon><Connection /></el-icon> 添加关系
      </div>
      <div class="menu-item" @click="onContextAction('history')">
        <el-icon><Clock /></el-icon> 变更历史
      </div>
      <div class="menu-divider" />
      <div class="menu-item danger" @click="onContextAction('delete')">
        <el-icon><Delete /></el-icon> 删除
      </div>
    </div>

    <!-- Tooltip -->
    <div
      v-if="tooltip.visible"
      class="graph-tooltip"
      :style="{ left: tooltip.x + 'px', top: tooltip.y + 'px' }"
    >
      <div class="tooltip-title">{{ tooltip.label }}</div>
      <div class="tooltip-type">
        <el-tag :color="tooltip.color" size="small" effect="dark">{{ tooltip.type }}</el-tag>
        <el-tag size="small" type="info">{{ tooltip.layer }}</el-tag>
      </div>
      <div v-if="tooltip.extra" class="tooltip-extra">{{ tooltip.extra }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, computed, nextTick, toRaw } from 'vue'
import { Graph } from '@antv/g6'
import { useGraphStore } from '@/stores/useGraphStore'
import { useSelectionStore } from '@/stores/useSelectionStore'
import { useDrawerStore } from '@/stores/useDrawerStore'
import { getNodeStyle, getEdgeStyle } from '@/components/graph/config/nodeStyles'

const graphStore = useGraphStore()
const selectionStore = useSelectionStore()
const drawerStore = useDrawerStore()

const containerRef = ref<HTMLElement | null>(null)
let graph: Graph | null = null

const layoutType = ref<'force' | 'concentric' | 'tree'>('force')

const nodeCount = computed(() => graphStore.graphData?.nodes?.length || 0)
const edgeCount = computed(() => graphStore.graphData?.edges?.length || 0)
const expandedLabel = computed(() => {
  if (!graphStore.expandedNodeId || !graphStore.graphData) return ''
  const node = graphStore.graphData.nodes.find(n => n.id === graphStore.expandedNodeId)
  return node?.data?.label || ''
})

// Context menu state
const contextMenu = ref({ visible: false, x: 0, y: 0, nodeId: '' })
// Tooltip state
const tooltip = ref({ visible: false, x: 0, y: 0, label: '', type: '', layer: '', color: '', extra: '' })

const layoutConfigs: Record<string, any> = {
  force: {
    type: 'd3-force',
    preventOverlap: true,
    nodeStrength: -200,
    edgeStrength: 0.1,
    collideStrength: 0.8,
    alphaDecay: 0.02,
  },
  concentric: {
    type: 'concentric',
    maxLevelDiff: 1,
    sortBy: 'degree',
    preventOverlap: true,
    nodeSize: 60,
  },
  tree: {
    type: 'dagre',
    rankdir: 'TB',
    nodesep: 40,
    ranksep: 60,
  },
}

onMounted(async () => {
  await nextTick()
  if (!containerRef.value) return

  graph = new Graph({
    container: containerRef.value,
    autoFit: 'view',
    padding: [40, 40, 60, 40],
    node: {
      style: (data: any) => getNodeStyle(data),
      state: {
        selected: { lineWidth: 3, stroke: '#3B82F6' },
        highlight: { lineWidth: 2, stroke: '#F59E0B' },
        dimmed: { opacity: 0.2 },
      },
    },
    edge: {
      style: (data: any) => getEdgeStyle(data),
      state: {
        selected: { lineWidth: 3 },
        highlight: { lineWidth: 2 },
        dimmed: { opacity: 0.1 },
      },
    },
    layout: layoutConfigs.force,
    behaviors: [
      'drag-canvas',
      'zoom-canvas',
      'drag-element',
      { type: 'click-select', multiple: false },
    ],
    animation: true,
  })

  // Bind events
  graph.on('node:click', (event: any) => {
    const id = event.target.id
    selectionStore.select(id, 'graph')
    contextMenu.value.visible = false
  })

  graph.on('node:dblclick', (event: any) => {
    const id = event.target.id
    graphStore.expandNode(id)
  })

  graph.on('node:contextmenu', (event: any) => {
    event.preventDefault?.()
    const { client } = event
    const containerRect = containerRef.value!.getBoundingClientRect()
    contextMenu.value = {
      visible: true,
      x: (client?.x || event.clientX || 200) - containerRect.left,
      y: (client?.y || event.clientY || 200) - containerRect.top,
      nodeId: event.target.id,
    }
  })

  graph.on('node:pointerenter', (event: any) => {
    const nodeData = graphStore.graphData?.nodes?.find(n => n.id === event.target.id)
    if (!nodeData) return
    const { client } = event
    const containerRect = containerRef.value!.getBoundingClientRect()
    const style = getNodeStyle(nodeData)
    tooltip.value = {
      visible: true,
      x: (client?.x || 200) - containerRect.left + 12,
      y: (client?.y || 200) - containerRect.top - 10,
      label: nodeData.data?.label || '',
      type: nodeData.data?.entityType || '',
      layer: nodeData.data?.layer || '',
      color: style.fill as string || '#3B82F6',
      extra: nodeData.data?.properties?.efficacy || nodeData.data?.properties?.riskLevel || '',
    }
  })

  graph.on('node:pointerleave', () => {
    tooltip.value.visible = false
  })

  graph.on('canvas:click', () => {
    selectionStore.clearSelection()
    contextMenu.value.visible = false
    tooltip.value.visible = false
  })

  // Load initial data
  await graphStore.loadGraphData()

  // Render
  if (graphStore.graphData) {
    graph.setData(toRaw(graphStore.graphData))
    await graph.render()
  }
})

// Watch for data changes
watch(
  () => graphStore.graphData,
  async (newData) => {
    if (!graph || !newData) return
    graph.setData(toRaw(newData))
    await graph.render()
  },
  { deep: false }
)

// Watch layout changes
watch(layoutType, (type) => {
  if (!graph) return
  graph.setLayout(layoutConfigs[type])
  graph.layout()
})

// Watch for external selection (from table)
watch(
  () => selectionStore.entityId,
  (id) => {
    if (!graph || selectionStore.source === 'graph') return
    if (id) {
      graph.setElementState(id, 'selected', true)
      graph.focusElement(id)
    }
  }
)

function setLayout(type: 'force' | 'concentric' | 'tree') {
  layoutType.value = type
}

function zoomIn() {
  graph?.zoomBy(1.2)
}

function zoomOut() {
  graph?.zoomBy(0.8)
}

function fitView() {
  graph?.fitView()
}

function onContextAction(action: string) {
  const nodeId = contextMenu.value.nodeId
  contextMenu.value.visible = false

  if (action === 'detail' || action === 'edit') {
    selectionStore.select(nodeId, 'graph')
    drawerStore.open(nodeId)
    if (action === 'edit') drawerStore.activeTab = 'properties'
  } else if (action === 'addRel') {
    selectionStore.select(nodeId, 'graph')
    drawerStore.open(nodeId)
    drawerStore.activeTab = 'relationships'
  } else if (action === 'history') {
    selectionStore.select(nodeId, 'graph')
    drawerStore.open(nodeId)
    drawerStore.activeTab = 'history'
  }
}

onUnmounted(() => {
  graph?.destroy()
  graph = null
})
</script>

<style scoped lang="scss">
.graph-canvas {
  width: 100%;
  height: 100%;
  position: relative;
  background: #FAFBFC;
  overflow: hidden;
}

.graph-toolbar {
  position: absolute;
  top: 8px;
  left: 8px;
  z-index: 10;
  display: flex;
  align-items: center;
  gap: 4px;
  background: rgba(255, 255, 255, 0.95);
  padding: 4px 8px;
  border-radius: 6px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
}

.node-count {
  font-size: 11px;
}

.graph-loading {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  background: rgba(255, 255, 255, 0.8);
  z-index: 20;
  color: #64748B;
}

.graph-empty {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 5;
}

.graph-breadcrumb {
  position: absolute;
  top: 8px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 10;
  background: rgba(255, 255, 255, 0.95);
  padding: 6px 16px;
  border-radius: 6px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
}

.graph-hint {
  position: absolute;
  bottom: 8px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 10;
  background: rgba(30, 41, 59, 0.6);
  color: #E2E8F0;
  padding: 4px 16px;
  border-radius: 4px;
  font-size: 12px;
  pointer-events: none;
}

.context-menu {
  position: absolute;
  z-index: 100;
  background: #FFFFFF;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
  padding: 4px 0;
  min-width: 160px;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  font-size: 13px;
  color: #334155;
  cursor: pointer;
  &:hover {
    background: #F1F5F9;
  }
  &.danger {
    color: #EF4444;
  }
}

.menu-divider {
  height: 1px;
  background: #E2E8F0;
  margin: 4px 0;
}

.graph-tooltip {
  position: absolute;
  z-index: 50;
  background: #FFFFFF;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  padding: 10px 14px;
  pointer-events: none;
  max-width: 240px;
}

.tooltip-title {
  font-size: 14px;
  font-weight: 600;
  color: #1E293B;
  margin-bottom: 6px;
}

.tooltip-type {
  display: flex;
  gap: 4px;
  margin-bottom: 4px;
}

.tooltip-extra {
  font-size: 12px;
  color: #64748B;
  margin-top: 4px;
}
</style>

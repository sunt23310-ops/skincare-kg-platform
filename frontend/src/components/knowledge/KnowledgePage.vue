<template>
  <div class="knowledge-page">
    <Splitpanes class="default-theme" @resize="onResize">
      <Pane :size="graphPaneSize" :min-size="30">
        <div class="graph-panel">
          <GraphCanvas ref="graphCanvasRef" />
        </div>
      </Pane>
      <Pane :size="100 - graphPaneSize" :min-size="30">
        <div class="table-panel">
          <DataTablePanel />
        </div>
      </Pane>
    </Splitpanes>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Splitpanes, Pane } from 'splitpanes'
import 'splitpanes/dist/splitpanes.css'
import GraphCanvas from '@/components/graph/GraphCanvas.vue'
import DataTablePanel from '@/components/table/DataTablePanel.vue'

const graphPaneSize = ref(45)
const graphCanvasRef = ref()

function onResize(event: any[]) {
  graphPaneSize.value = event[0].size
}
</script>

<style scoped lang="scss">
.knowledge-page {
  flex: 1;
  overflow: hidden;
}

.graph-panel, .table-panel {
  height: 100%;
  overflow: hidden;
}

:deep(.splitpanes__splitter) {
  background: #E2E8F0;
  width: 4px;
  &:hover {
    background: #3B82F6;
  }
}
</style>

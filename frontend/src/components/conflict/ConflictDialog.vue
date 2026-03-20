<template>
  <el-dialog v-model="visible" title="冲突校验结果" width="600px">
    <div v-if="loading" class="loading-state">
      <el-icon class="is-loading" :size="32"><Loading /></el-icon>
      <span>正在检测成分冲突...</span>
    </div>
    <div v-else>
      <el-result
        v-if="conflicts.length === 0"
        icon="success"
        title="无冲突"
        sub-title="当前视图内所有成分关系正常，未发现冲突。"
      />
      <div v-else>
        <el-alert
          :title="`发现 ${conflicts.length} 对冲突关系`"
          type="warning"
          :closable="false"
          show-icon
          style="margin-bottom: 16px"
        />
        <div v-for="(conflict, i) in conflicts" :key="i" class="conflict-item">
          <div class="conflict-pair">
            <el-tag type="primary" size="small">{{ conflict.source }}</el-tag>
            <span class="conflict-icon">⚡</span>
            <el-tag type="primary" size="small">{{ conflict.target }}</el-tag>
          </div>
          <div class="conflict-detail">
            <el-tag type="danger" size="small">{{ conflict.constraintType }}</el-tag>
            <span v-if="conflict.interval" class="interval">间隔: {{ conflict.interval }}</span>
          </div>
          <div class="conflict-note">{{ conflict.note }}</div>
        </div>
      </div>
    </div>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useGraphStore } from '@/stores/useGraphStore'

const visible = defineModel<boolean>({ default: false })
const graphStore = useGraphStore()
const loading = ref(false)

const conflicts = computed(() => {
  const edges = graphStore.allEdges || []
  return edges
    .filter((e: any) => e.data?.relType === 'conflicts_with')
    .map((e: any) => {
      const srcNode = graphStore.allNodes?.find((n: any) => n.id === e.source)
      const tgtNode = graphStore.allNodes?.find((n: any) => n.id === e.target)
      return {
        source: srcNode?.data?.label || e.source,
        target: tgtNode?.data?.label || e.target,
        constraintType: e.data?.properties?.constraint_type || '冲突',
        interval: e.data?.properties?.interval || '',
        note: e.data?.properties?.note || '',
      }
    })
})

watch(visible, (val) => {
  if (val) {
    loading.value = true
    setTimeout(() => { loading.value = false }, 500)
  }
})
</script>

<style scoped lang="scss">
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 40px;
  color: #64748B;
}

.conflict-item {
  padding: 12px;
  border: 1px solid #FEE2E2;
  border-radius: 8px;
  margin-bottom: 8px;
  background: #FFF5F5;
}

.conflict-pair {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}

.conflict-icon {
  font-size: 16px;
}

.conflict-detail {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.interval {
  font-size: 12px;
  color: #64748B;
}

.conflict-note {
  font-size: 13px;
  color: #475569;
}
</style>

<template>
  <div class="knowledge-view">
    <ToolbarPanel />
    <KnowledgePage />
    <EntityDrawer />
    <RelationshipMatrix />
    <ConflictDialog />
  </div>
</template>

<script setup lang="ts">
import ToolbarPanel from '@/components/knowledge/ToolbarPanel.vue'
import KnowledgePage from '@/components/knowledge/KnowledgePage.vue'
import EntityDrawer from '@/components/drawer/EntityDrawer.vue'
import RelationshipMatrix from '@/components/matrix/RelationshipMatrix.vue'
import ConflictDialog from '@/components/conflict/ConflictDialog.vue'
import { useThreeWaySync } from '@/composables/useThreeWaySync'

// Activate three-way linking
useThreeWaySync()
</script>

<style scoped lang="scss">
.knowledge-view {
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
</style>

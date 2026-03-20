<template>
  <div class="toolbar-panel">
    <!-- Row 1: Filters + Actions -->
    <div class="toolbar-row">
      <div class="filters">
        <el-select
          v-model="filterStore.layer"
          placeholder="选择层级"
          style="width: 160px"
          @change="filterStore.setLayer"
        >
          <el-option-group
            v-for="group in layerGroups"
            :key="group.label"
            :label="group.label"
          >
            <el-option
              v-for="item in group.items"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-option-group>
        </el-select>

        <el-select
          v-model="selectedEntityType"
          placeholder="实体类型"
          style="width: 140px"
          clearable
          @change="onEntityTypeChange"
        >
          <el-option
            v-for="t in entityTypeOptions"
            :key="t.value"
            :label="t.label"
            :value="t.value"
          />
        </el-select>

        <el-input
          v-model="filterStore.searchQuery"
          placeholder="搜索名称、别名、ID..."
          :prefix-icon="Search"
          clearable
          style="width: 240px"
          @input="onSearchDebounced"
        />
      </div>

      <div class="actions">
        <el-button :icon="Upload" @click="$emit('import')">导入</el-button>
        <el-button :icon="Download" @click="$emit('export')">导出</el-button>
        <el-button
          v-if="filterStore.layer === 'L2'"
          type="primary"
          plain
          :icon="Grid"
          @click="matrixVisible = true"
        >
          关系矩阵
        </el-button>
        <el-button
          type="primary"
          :icon="CircleCheck"
          @click="conflictVisible = true"
        >
          冲突校验
        </el-button>
        <el-button type="success" :icon="Plus" @click="$emit('create')">
          新增
        </el-button>
      </div>
    </div>

    <!-- Row 2: Relationship Category Tags -->
    <div class="rel-filter-row">
      <span class="rel-label">关系分类：</span>
      <div class="rel-tags">
        <el-check-tag
          v-for="cat in relCategories"
          :key="cat.key"
          :checked="filterStore.relCategories.includes(cat.key)"
          :style="getTagStyle(cat, filterStore.relCategories.includes(cat.key))"
          @change="filterStore.toggleRelCategory(cat.key)"
        >
          {{ cat.label }}
          <span class="tag-count">{{ cat.count }}</span>
        </el-check-tag>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, inject, type Ref } from 'vue'
import { Search, Upload, Download, Grid, CircleCheck, Plus } from '@element-plus/icons-vue'
import { useFilterStore } from '@/stores/useFilterStore'
import { useDebounceFn } from '@vueuse/core'
import type { RelCategory } from '@/types'

const filterStore = useFilterStore()

const matrixVisible = inject<Ref<boolean>>('matrixVisible', ref(false))
const conflictVisible = inject<Ref<boolean>>('conflictVisible', ref(false))

const selectedEntityType = ref('')

const layerGroups = [
  {
    label: '基础层',
    items: [
      { value: 'L0', label: 'L0 画像配置' },
      { value: 'L1', label: 'L1 商品' },
    ],
  },
  {
    label: '知识层',
    items: [
      { value: 'L2', label: 'L2 知识' },
      { value: 'L3', label: 'L3 方案' },
    ],
  },
  {
    label: '引擎层',
    items: [
      { value: 'L4', label: 'L4 对话' },
      { value: 'L5', label: 'L5 词汇' },
    ],
  },
]

const entityTypeMap: Record<string, { value: string; label: string }[]> = {
  L0: [
    { value: 'SkinType', label: '肤质' },
    { value: 'Concern', label: '诉求' },
    { value: 'Budget', label: '预算' },
    { value: 'Scenario', label: '场景' },
  ],
  L1: [
    { value: 'Brand', label: '品牌' },
    { value: 'SPU', label: 'SPU商品' },
  ],
  L2: [
    { value: 'Ingredient', label: '成分' },
    { value: 'Efficacy', label: '功效' },
    { value: 'Symptom', label: '症状' },
    { value: 'AdverseReaction', label: '不良反应' },
  ],
  L3: [
    { value: 'SkincarePlan', label: '方案' },
  ],
  L4: [
    { value: 'Intent', label: '意图' },
  ],
  L5: [
    { value: 'SynonymMapping', label: '同义词' },
  ],
}

const entityTypeOptions = computed(() => (filterStore.layer ? entityTypeMap[filterStore.layer] : []) || [])

const relCategories = [
  { key: '等价映射' as RelCategory, label: '等价映射', color: '#94A3B8', count: 158 },
  { key: '替代递进' as RelCategory, label: '替代递进', color: '#06B6D4', count: 1 },
  { key: '协同增强' as RelCategory, label: '协同增强', color: '#22C55E', count: 12 },
  { key: '互斥约束' as RelCategory, label: '互斥约束', color: '#EF4444', count: 27 },
  { key: '因果归因' as RelCategory, label: '因果归因', color: '#6366F1', count: 160 },
  { key: '组成归属' as RelCategory, label: '组成归属', color: '#94A3B8', count: 71 },
]

function getTagStyle(cat: typeof relCategories[0], checked: boolean) {
  if (checked) {
    return {
      background: cat.color + '20',
      borderColor: cat.color,
      color: cat.color,
    }
  }
  return {
    background: 'transparent',
    borderColor: '#E2E8F0',
    color: '#94A3B8',
  }
}

function onEntityTypeChange(val: string) {
  if (val) {
    filterStore.entityTypes = [val]
  } else {
    filterStore.entityTypes = []
  }
}

const onSearchDebounced = useDebounceFn(() => {
  filterStore.setSearch(filterStore.searchQuery)
}, 300)

defineEmits(['import', 'export', 'create'])
</script>

<style scoped lang="scss">
.toolbar-panel {
  background: #FFFFFF;
  border-bottom: 1px solid #E2E8F0;
  padding: 12px 16px;
  flex-shrink: 0;
}

.toolbar-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.filters {
  display: flex;
  align-items: center;
  gap: 8px;
}

.actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.rel-filter-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid #F1F5F9;
}

.rel-label {
  font-size: 13px;
  color: #64748B;
  white-space: nowrap;
}

.rel-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.el-check-tag {
  border: 1px solid;
  border-radius: 4px;
  padding: 2px 10px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
  user-select: none;
}

.tag-count {
  margin-left: 4px;
  font-size: 11px;
  opacity: 0.7;
}
</style>

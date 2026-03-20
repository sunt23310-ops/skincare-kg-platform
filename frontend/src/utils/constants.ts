// ============================================================
// Skincare Knowledge Graph Platform - Constants & Configuration
// ============================================================

import type {
  LayerTabDef,
  RelCategoryConfig,
  RelTypeConfig,
  EntityTypeStyle,
  RelCategory,
} from '@/types'

// ============================================================
// LAYER_TABS - Complete tab structure with sub-tabs & columns
// ============================================================

export const LAYER_TABS: LayerTabDef[] = [
  // -------------------- L0: 用户画像层 --------------------
  {
    layer: 'L0',
    label: 'L0 用户画像',
    group: '基础层',
    subTabs: [
      {
        key: 'skin-type',
        label: '肤质枚举',
        entityType: 'SkinType',
        columns: [
          { prop: 'label', label: '肤质名称', width: 140, sortable: true },
          { prop: 'code', label: '编码', width: 120 },
        ],
      },
      {
        key: 'concern',
        label: '诉求体系',
        entityType: 'Concern',
        columns: [
          { prop: 'label', label: '诉求名称', width: 140, sortable: true },
          { prop: 'code', label: '编码', width: 120 },
        ],
      },
      {
        key: 'budget',
        label: '预算档位',
        entityType: 'Budget',
        columns: [
          { prop: 'label', label: '档位名称', width: 200, sortable: true },
          { prop: 'code', label: '编码', width: 120 },
        ],
      },
    ],
  },

  // -------------------- L1: 商品层 --------------------
  {
    layer: 'L1',
    label: 'L1 商品',
    group: '基础层',
    subTabs: [
      {
        key: 'brand',
        label: '品牌管理',
        entityType: 'Brand',
        columns: [
          { prop: 'label', label: '品牌名称', width: 140, sortable: true },
          { prop: 'labelEn', label: '英文名', width: 140 },
          { prop: 'tier', label: '定位', width: 160, type: 'tag' },
          { prop: 'code', label: '编码', width: 120 },
        ],
      },
      {
        key: 'sku',
        label: 'SKU列表',
        entityType: 'SKU',
        columns: [
          { prop: 'label', label: 'SKU名称', width: 200, sortable: true },
          { prop: 'brand', label: '品牌', width: 120 },
          { prop: 'category', label: '品类', width: 100, type: 'tag' },
          { prop: 'aliases', label: '昵称', width: 160, type: 'tag' },
          { prop: 'keyIngredients', label: '核心成分', width: 200 },
        ],
      },
    ],
  },

  // -------------------- L2: 知识层 --------------------
  {
    layer: 'L2',
    label: 'L2 成分/功效',
    group: '知识层',
    subTabs: [
      {
        key: 'ingredient',
        label: '成分库',
        entityType: 'Ingredient',
        columns: [
          { prop: 'label', label: '成分名称', width: 160, sortable: true },
          { prop: 'labelEn', label: '英文名', width: 200 },
          { prop: 'riskLevel', label: '安全等级', width: 100, type: 'status' },
          { prop: 'efficacy', label: '功效', width: 200 },
          { prop: 'aliases', label: '别名', width: 160, type: 'tag' },
        ],
      },
      {
        key: 'efficacy',
        label: '功效标签',
        entityType: 'Efficacy',
        columns: [
          { prop: 'label', label: '功效名称', width: 140, sortable: true },
          { prop: 'code', label: '编码', width: 160 },
        ],
      },
      {
        key: 'symptom',
        label: '症状库',
        entityType: 'Symptom',
        columns: [
          { prop: 'label', label: '症状名称', width: 140, sortable: true },
          { prop: 'code', label: '编码', width: 120 },
          { prop: 'concern', label: '关联诉求', width: 200 },
        ],
      },
      {
        key: 'adverse-reaction',
        label: '不良反应',
        entityType: 'AdverseReaction',
        columns: [
          { prop: 'label', label: '反应名称', width: 140, sortable: true },
          { prop: 'severity', label: '严重程度', width: 120, type: 'tag' },
          { prop: 'code', label: '编码', width: 120 },
        ],
      },
    ],
  },

  // -------------------- L3: 方案层 --------------------
  {
    layer: 'L3',
    label: 'L3 方案',
    group: '知识层',
    subTabs: [
      {
        key: 'skincare-plan',
        label: '护肤方案',
        entityType: 'SkincarePlan',
        columns: [
          { prop: 'label', label: '方案名称', width: 200, sortable: true },
          { prop: 'suitableSkin', label: '适用肤质', width: 140 },
          { prop: 'targetConcern', label: '目标诉求', width: 120 },
          { prop: 'steps', label: '步骤', width: 280, type: 'tag' },
        ],
      },
    ],
  },

  // -------------------- L4: 对话引擎层 --------------------
  {
    layer: 'L4',
    label: 'L4 对话引擎',
    group: '引擎层',
    subTabs: [
      {
        key: 'intent-tree',
        label: '意图树',
        entityType: 'Intent',
        columns: [
          { prop: 'label', label: '意图名称', width: 160, sortable: true },
          { prop: 'channel', label: '渠道', width: 100, type: 'tag' },
          { prop: 'priority', label: '优先级', width: 80, sortable: true },
          { prop: 'code', label: '编码', width: 160 },
        ],
      },
    ],
  },

  // -------------------- L5: 词典层 --------------------
  {
    layer: 'L5',
    label: 'L5 词典',
    group: '引擎层',
    subTabs: [
      {
        key: 'synonym',
        label: '同义词映射',
        entityType: 'SynonymMapping',
        columns: [
          { prop: 'label', label: '标准词', width: 140, sortable: true },
          { prop: 'canonical', label: '规范名', width: 120 },
          { prop: 'variants', label: '同义词列表', width: 300, type: 'tag' },
          { prop: 'target', label: '映射目标', width: 140 },
        ],
      },
    ],
  },
]

// ============================================================
// REL_CATEGORIES - 6 relationship categories
// ============================================================

export const REL_CATEGORIES: RelCategoryConfig[] = [
  {
    category: '等价映射',
    color: '#6366F1',
    icon: 'Link',
    description: '两个实体语义等价或标准化映射关系',
  },
  {
    category: '替代递进',
    color: '#3B82F6',
    icon: 'Switch',
    description: '实体之间存在替代或升级迭代关系',
  },
  {
    category: '协同增强',
    color: '#10B981',
    icon: 'Connection',
    description: '实体之间存在正向协同或搭配增强效果',
  },
  {
    category: '互斥约束',
    color: '#EF4444',
    icon: 'Warning',
    description: '实体之间存在冲突、风险或耐受约束',
  },
  {
    category: '因果归因',
    color: '#F59E0B',
    icon: 'Right',
    description: '实体之间存在功效、治疗、诱因或指示关系',
  },
  {
    category: '组成归属',
    color: '#8B5CF6',
    icon: 'FolderOpened',
    description: '实体之间存在包含或组成关系',
  },
]

// ============================================================
// REL_TYPE_CONFIG - 13 relationship types
// ============================================================

export const REL_TYPE_CONFIG: RelTypeConfig[] = [
  // 等价映射
  {
    relType: 'maps_to',
    category: '等价映射',
    lineStyle: 'solid',
    color: '#6366F1',
    label: '映射到',
    directionality: 'directed',
    polarity: 'neutral',
  },

  // 替代递进
  {
    relType: 'substitutes_for',
    category: '替代递进',
    lineStyle: 'dashed',
    color: '#3B82F6',
    label: '可替代',
    directionality: 'directed',
    polarity: 'neutral',
  },
  {
    relType: 'upgrades_to',
    category: '替代递进',
    lineStyle: 'solid',
    color: '#3B82F6',
    label: '升级为',
    directionality: 'directed',
    polarity: 'positive',
  },

  // 协同增强
  {
    relType: 'synergizes_with',
    category: '协同增强',
    lineStyle: 'solid',
    color: '#10B981',
    label: '协同增效',
    directionality: 'undirected',
    polarity: 'positive',
  },
  {
    relType: 'often_paired_with',
    category: '协同增强',
    lineStyle: 'dashed',
    color: '#10B981',
    label: '常搭配',
    directionality: 'undirected',
    polarity: 'positive',
  },

  // 互斥约束
  {
    relType: 'conflicts_with',
    category: '互斥约束',
    lineStyle: 'solid',
    color: '#EF4444',
    label: '冲突',
    directionality: 'undirected',
    polarity: 'negative',
  },
  {
    relType: 'risk_for',
    category: '互斥约束',
    lineStyle: 'dashed',
    color: '#EF4444',
    label: '有风险',
    directionality: 'directed',
    polarity: 'negative',
  },
  {
    relType: 'requires_tolerance',
    category: '互斥约束',
    lineStyle: 'dotted',
    color: '#EF4444',
    label: '需建立耐受',
    directionality: 'directed',
    polarity: 'negative',
  },

  // 因果归因
  {
    relType: 'has_efficacy',
    category: '因果归因',
    lineStyle: 'solid',
    color: '#F59E0B',
    label: '具有功效',
    directionality: 'directed',
    polarity: 'positive',
  },
  {
    relType: 'resolves',
    category: '因果归因',
    lineStyle: 'solid',
    color: '#F59E0B',
    label: '可解决',
    directionality: 'directed',
    polarity: 'positive',
  },
  {
    relType: 'triggered_by',
    category: '因果归因',
    lineStyle: 'dashed',
    color: '#F59E0B',
    label: '由…触发',
    directionality: 'directed',
    polarity: 'negative',
  },
  {
    relType: 'indicates',
    category: '因果归因',
    lineStyle: 'dotted',
    color: '#F59E0B',
    label: '指示',
    directionality: 'directed',
    polarity: 'neutral',
  },

  // 组成归属
  {
    relType: 'contains',
    category: '组成归属',
    lineStyle: 'solid',
    color: '#8B5CF6',
    label: '包含',
    directionality: 'directed',
    polarity: 'neutral',
  },
]

// ============================================================
// ENTITY_TYPE_STYLES - 8 entity type visual styles
// ============================================================

export const ENTITY_TYPE_STYLES: EntityTypeStyle[] = [
  { entityType: 'Ingredient', shape: 'circle', color: '#3B82F6', size: 64 },
  { entityType: 'Efficacy', shape: 'circle', color: '#6366F1', size: 48 },
  { entityType: 'Concern', shape: 'circle', color: '#8B5CF6', size: 44 },
  { entityType: 'Symptom', shape: 'circle', color: '#F59E0B', size: 40 },
  { entityType: 'Brand', shape: 'rect', color: '#94A3B8', size: 56 },
  { entityType: 'SKU', shape: 'rect', color: '#CBD5E1', size: 40 },
  { entityType: 'SkincarePlan', shape: 'hexagon', color: '#A855F7', size: 56 },
  { entityType: 'LexiconEntry', shape: 'circle', color: '#06B6D4', size: 32 },
]

// ============================================================
// Helper lookup maps
// ============================================================

/** Quick lookup: relType -> RelTypeConfig */
export const REL_TYPE_MAP = new Map(
  REL_TYPE_CONFIG.map((c) => [c.relType, c])
)

/** Quick lookup: category name -> RelCategoryConfig */
export const REL_CATEGORY_MAP = new Map(
  REL_CATEGORIES.map((c) => [c.category, c])
)

/** Quick lookup: entityType -> EntityTypeStyle */
export const ENTITY_STYLE_MAP = new Map(
  ENTITY_TYPE_STYLES.map((s) => [s.entityType, s])
)

/** All 6 category names */
export const ALL_REL_CATEGORIES: RelCategory[] = REL_CATEGORIES.map(
  (c) => c.category
)

// ============================================================
// Skincare Knowledge Graph Platform - Type Definitions
// ============================================================

// --- Layer codes ---
export type LayerCode = 'L0' | 'L1' | 'L2' | 'L3' | 'L4' | 'L5'

// --- 6 relationship categories ---
export type RelCategory =
  | '等价映射'
  | '替代递进'
  | '协同增强'
  | '互斥约束'
  | '因果归因'
  | '组成归属'

// --- 13 relationship types ---
export type RelType =
  | 'maps_to'
  | 'substitutes_for'
  | 'upgrades_to'
  | 'synergizes_with'
  | 'often_paired_with'
  | 'conflicts_with'
  | 'risk_for'
  | 'requires_tolerance'
  | 'has_efficacy'
  | 'resolves'
  | 'triggered_by'
  | 'indicates'
  | 'contains'

// --- G6 node data ---
export interface G6NodeData {
  id: string
  data: {
    label: string
    labelEn?: string
    layer: LayerCode
    entityType: string
    properties: Record<string, any>
  }
}

// --- G6 edge data ---
export interface G6EdgeData {
  id: string
  source: string
  target: string
  data: {
    relType: RelType
    category: RelCategory
    label: string
    properties: {
      constraint_type?: string
      interval?: string
      condition?: string
      confidence?: string
      evidence?: string
      note?: string
    }
  }
}

// --- G6 full graph data ---
export interface G6GraphData {
  nodes: G6NodeData[]
  edges: G6EdgeData[]
}

// --- Graph query parameters ---
export interface GraphQueryParams {
  layer?: LayerCode
  entityTypes?: string[]
  search?: string
  relCategories?: RelCategory[]
}

// --- Entity detail for drawer ---
export interface EntityDetail {
  id: string
  label: string
  layer: LayerCode
  entityType: string
  properties: Record<string, any>
  relationships: G6EdgeData[]
}

// --- Table column definition ---
export interface TableColumnDef {
  prop: string
  label: string
  width?: number
  sortable?: boolean
  formatter?: (row: any) => string
  type?: 'tag' | 'status' | 'link'
}

// --- Sub-tab definition ---
export interface SubTabDef {
  key: string
  label: string
  entityType: string
  columns: TableColumnDef[]
}

// --- Layer tab definition ---
export interface LayerTabDef {
  layer: LayerCode
  label: string
  group: '基础层' | '知识层' | '引擎层'
  subTabs: SubTabDef[]
}

// --- Relationship category config ---
export interface RelCategoryConfig {
  category: RelCategory
  color: string
  icon: string
  description: string
}

// --- Relationship type config ---
export interface RelTypeConfig {
  relType: RelType
  category: RelCategory
  lineStyle: 'solid' | 'dashed' | 'dotted'
  color: string
  label: string
  directionality: 'directed' | 'undirected'
  polarity: 'positive' | 'negative' | 'neutral'
}

// --- Entity type visual style ---
export interface EntityTypeStyle {
  entityType: string
  shape: 'circle' | 'rect' | 'hexagon'
  color: string
  size: number | [number, number]
}

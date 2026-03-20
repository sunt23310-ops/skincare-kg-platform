import type { RelCategory } from '@/types'

// Entity type → G6 node style mapping (per design spec)
const ENTITY_STYLES: Record<string, { type: string; fill: string; size: number; labelFill: string }> = {
  Ingredient:       { type: 'circle', fill: '#3B82F6', size: 48, labelFill: '#FFFFFF' },
  Efficacy:         { type: 'circle', fill: '#6366F1', size: 40, labelFill: '#FFFFFF' },
  Concern:          { type: 'circle', fill: '#8B5CF6', size: 36, labelFill: '#FFFFFF' },
  Symptom:          { type: 'circle', fill: '#F59E0B', size: 36, labelFill: '#FFFFFF' },
  AdverseReaction:  { type: 'circle', fill: '#EF4444', size: 36, labelFill: '#FFFFFF' },
  Brand:            { type: 'rect',   fill: '#94A3B8', size: 48, labelFill: '#FFFFFF' },
  SKU:              { type: 'rect',   fill: '#CBD5E1', size: 36, labelFill: '#334155' },
  SkincarePlan:     { type: 'diamond',fill: '#A855F7', size: 48, labelFill: '#FFFFFF' },
  AftersalesPlan:   { type: 'diamond',fill: '#EC4899', size: 40, labelFill: '#FFFFFF' },
  MakeupPlan:       { type: 'diamond',fill: '#F472B6', size: 40, labelFill: '#FFFFFF' },
  SkinType:         { type: 'circle', fill: '#10B981', size: 36, labelFill: '#FFFFFF' },
  Budget:           { type: 'rect',   fill: '#F59E0B', size: 32, labelFill: '#FFFFFF' },
  Scenario:         { type: 'circle', fill: '#8B5CF6', size: 32, labelFill: '#FFFFFF' },
  Intent:           { type: 'rect',   fill: '#F97316', size: 36, labelFill: '#FFFFFF' },
  RouteSignal:      { type: 'circle', fill: '#14B8A6', size: 32, labelFill: '#FFFFFF' },
  SynonymMapping:   { type: 'circle', fill: '#06B6D4', size: 28, labelFill: '#FFFFFF' },
  HotWord:          { type: 'circle', fill: '#06B6D4', size: 24, labelFill: '#FFFFFF' },
}

// Relationship type → edge style mapping
const REL_STYLES: Record<string, { color: string; dash?: number[]; width: number; label: string }> = {
  conflicts_with:     { color: '#EF4444', dash: [6, 4], width: 2, label: '冲突' },
  risk_for:           { color: '#F59E0B', dash: [6, 4], width: 1.5, label: '风险' },
  requires_tolerance: { color: '#F59E0B', dash: [3, 3], width: 1.5, label: '耐受' },
  synergizes_with:    { color: '#22C55E', width: 2, label: '协同' },
  often_paired_with:  { color: '#22C55E', width: 1.5, label: '搭配' },
  has_efficacy:       { color: '#6366F1', width: 2, label: '功效' },
  resolves:           { color: '#6366F1', width: 1.5, label: '解决' },
  triggered_by:       { color: '#6366F1', dash: [4, 3], width: 1.5, label: '触发' },
  indicates:          { color: '#6366F1', dash: [4, 3], width: 1, label: '暗示' },
  substitutes_for:    { color: '#06B6D4', dash: [3, 3], width: 1.5, label: '平替' },
  upgrades_to:        { color: '#06B6D4', dash: [3, 3], width: 1.5, label: '升级' },
  contains:           { color: '#94A3B8', width: 1, label: '含有' },
  maps_to:            { color: '#94A3B8', dash: [4, 4], width: 1, label: '映射' },
}

// Symmetric relationship types (create both directions)
export const SYMMETRIC_RELS = ['conflicts_with', 'synergizes_with', 'substitutes_for', 'often_paired_with']

// Relationship type → category mapping
export const REL_TYPE_TO_CATEGORY: Record<string, RelCategory> = {
  maps_to: '等价映射',
  substitutes_for: '替代递进',
  upgrades_to: '替代递进',
  synergizes_with: '协同增强',
  often_paired_with: '协同增强',
  conflicts_with: '互斥约束',
  risk_for: '互斥约束',
  requires_tolerance: '互斥约束',
  has_efficacy: '因果归因',
  resolves: '因果归因',
  triggered_by: '因果归因',
  indicates: '因果归因',
  contains: '组成归属',
}

export function getNodeStyle(nodeData: any): Record<string, any> {
  const entityType = nodeData?.data?.entityType || 'Ingredient'
  const style = ENTITY_STYLES[entityType] || ENTITY_STYLES.Ingredient
  const label = nodeData?.data?.label || ''

  // Dynamic size based on relationship count
  let size = style.size
  const relCount = nodeData?.data?.properties?.relCount
  if (entityType === 'Ingredient' && relCount) {
    size = Math.min(80, Math.max(48, 48 + relCount * 2))
  }

  return {
    type: style.type,
    size,
    fill: style.fill,
    stroke: style.fill,
    lineWidth: 1,
    labelText: label.length > 6 ? label.slice(0, 6) + '…' : label,
    labelFill: style.labelFill,
    labelFontSize: size > 40 ? 11 : 10,
    labelPlacement: 'center',
    labelMaxWidth: size * 1.5,
    cursor: 'pointer',
    shadowColor: 'rgba(0,0,0,0.08)',
    shadowBlur: 4,
    shadowOffsetY: 2,
    radius: style.type === 'rect' ? 4 : undefined,
  }
}

export function getEdgeStyle(edgeData: any): Record<string, any> {
  const relType = edgeData?.data?.relType || 'has_efficacy'
  const style = REL_STYLES[relType] || { color: '#94A3B8', width: 1, label: '' }
  const isSymmetric = SYMMETRIC_RELS.includes(relType)

  return {
    stroke: style.color,
    lineWidth: style.width,
    lineDash: style.dash || undefined,
    endArrow: !isSymmetric,
    startArrow: false,
    labelText: style.label,
    labelFill: style.color,
    labelFontSize: 10,
    labelBackground: true,
    labelBackgroundFill: 'rgba(255,255,255,0.85)',
    labelBackgroundRadius: 2,
    labelBackgroundPadding: [1, 4, 1, 4],
    cursor: 'pointer',
  }
}

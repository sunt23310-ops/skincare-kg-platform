# 护肤知识图谱 — 数据格式规范

## 一、数据文件

项目使用两个静态 JSON 文件，位于 `frontend/src/data/`：

| 文件 | 内容 | 当前规模 |
|------|------|----------|
| `nodes.json` | 所有实体节点 | **617 个** |
| `edges.json` | 所有关系边 | **345 条** |

---

## 二、节点格式 (nodes.json)

```json
{
  "id": "L2_Ingredient_retinol",
  "data": {
    "label": "A醇/视黄醇",
    "labelEn": "Retinol",
    "layer": "L2",
    "entityType": "Ingredient",
    "properties": {
      "code": "retinol",
      "riskLevel": "caution",
      "efficacy": "抗老、淡纹、促进代谢",
      "aliases": ["A醇", "视黄醇"]
    }
  }
}
```

### ID 规则

`{层}_{实体类型}_{code}`，例如 `L2_Ingredient_retinol`、`L1_Brand_proya`

### 6 层 × 12 种实体类型

| 层 | 实体类型 | 数量 | 特有属性 |
|----|---------|------|---------|
| L0 | SkinType | 15 | — |
| L0 | Concern | 118 | — |
| L0 | Budget | 13 | — |
| L1 | Brand | 72 | `tier`（档次：international_luxury / international_mid / international_affordable / domestic_premium / domestic_affordable / functional） |
| L1 | SPU | 65 | `brand`, `category`, `aliases`, `keyIngredients` |
| L2 | Ingredient | 56 | `riskLevel`（safe / mild_caution / caution）, `efficacy`, `aliases` |
| L2 | Efficacy | 21 | — |
| L2 | Symptom | 34 | `concern` |
| L2 | AdverseReaction | 10 | `severity`（mild / mild-moderate / moderate-severe / severe） |
| L3 | SkincarePlan | 16 | `steps`（数组）, `suitableSkin`, `targetConcern` |
| L4 | Intent | 35 | `channel`, `priority` |
| L5 | SynonymMapping | 162 | `canonical`, `variants`（数组）, `target` |

### 必填字段

- `id`: 唯一标识，遵循 `{层}_{实体类型}_{code}` 格式
- `data.label`: 中文名称
- `data.layer`: 所属层（L0 ~ L5）
- `data.entityType`: 实体类型
- `data.properties.code`: 英文编码（小写+下划线）

### 可选字段

- `data.labelEn`: 英文名称
- `data.properties.*`: 按实体类型不同，附加不同属性

---

## 三、关系格式 (edges.json)

```json
{
  "id": "edge_0001",
  "source": "L2_Ingredient_retinol",
  "target": "L2_Ingredient_aha",
  "data": {
    "relType": "conflicts_with",
    "category": "互斥约束",
    "label": "冲突",
    "properties": {
      "constraint_type": "需间隔使用",
      "interval": "12h+",
      "note": "同时用刺激过大，可能损伤屏障"
    }
  }
}
```

### ID 规则

`edge_{四位自增编号}`，例如 `edge_0001`、`edge_0135`

### 必填字段

- `id`: 唯一标识
- `source`: 起点节点 id（必须存在于 nodes.json）
- `target`: 终点节点 id（必须存在于 nodes.json）
- `data.relType`: 关系类型（见下表）
- `data.category`: 关系分类（6 大分类之一）
- `data.label`: 显示标签

### 7 种关系类型（当前已有）

| relType | category | 数量 | properties 字段 |
|---------|----------|------|----------------|
| `has_efficacy` | 因果归因 | 63 | — |
| `contains` | 组成归属 | 28 | — |
| `maps_to` | 等价映射 | 15 | — |
| `synergizes_with` | 协同增强 | 11 | `note` |
| `risk_for` | 互斥约束 | 8 | `constraint_type`, `condition` |
| `conflicts_with` | 互斥约束 | 5 | `constraint_type`, `interval`, `note` |
| `requires_tolerance` | 互斥约束 | 5 | `interval`, `note`, `constraint_type` |

### 完整 13 种关系类型（架构预留）

| relType | category | 方向性 | 说明 |
|---------|----------|--------|------|
| `maps_to` | 等价映射 | 有向 | 同义词映射 |
| `substitutes_for` | 替代递进 | 对称 | 可替代 |
| `upgrades_to` | 替代递进 | 有向 | 升级替代 |
| `synergizes_with` | 协同增强 | 对称 | 协同增效 |
| `often_paired_with` | 协同增强 | 对称 | 常搭配 |
| `conflicts_with` | 互斥约束 | 对称 | 冲突 |
| `risk_for` | 互斥约束 | 有向 | 风险 |
| `requires_tolerance` | 互斥约束 | 自环 | 需耐受 |
| `has_efficacy` | 因果归因 | 有向 | 功效 |
| `resolves` | 因果归因 | 有向 | 解决症状 |
| `triggered_by` | 因果归因 | 有向 | 触发 |
| `indicates` | 因果归因 | 有向 | 指示 |
| `contains` | 组成归属 | 有向 | 包含 |

### 6 大关系分类颜色

| 分类 | 颜色 |
|------|------|
| 等价映射 | `#94A3B8`（灰色） |
| 替代递进 | `#06B6D4`（青色） |
| 协同增强 | `#22C55E`（绿色） |
| 互斥约束 | `#EF4444`（红色） |
| 因果归因 | `#6366F1`（紫色） |
| 组成归属 | `#F97316`（橙色） |

---

## 四、维护更新方式

### 方式 A：编辑 Python 脚本（推荐）

修改 `scripts/parse_vocab.py`，在对应字典/列表中添加数据，然后执行：

```bash
cd /Users/sunzhuoqi/Desktop/skincare-kg-platform

# 1. 重新生成 JSON
python3 scripts/parse_vocab.py

# 2. 构建验证
cd frontend && npm run build

# 3. 提交并推送（Vercel 自动部署）
cd ..
git add -A
git commit -m "update: 新增xxx数据"
git push
```

#### 添加成分示例

在 `ingredients` 字典中追加：

```python
"new_ingredient": ("中文名", "English Name", "safe", "功效描述", ["别名1", "别名2"]),
```

在 `efficacy_map` 中追加功效关系：

```python
"new_ingredient": ["hydrating", "soothing"],
```

#### 添加品牌示例

在 `brands` 列表中追加：

```python
("brand_code", "中文名", "English Name", "tier"),
```

#### 添加 SKU 示例

在 `skus` 列表中追加：

```python
("sku_code", "产品名", "brand_code", "品类", ["昵称"], "key_ingredient1,key_ingredient2"),
```

### 方式 B：直接编辑 JSON

直接修改 `frontend/src/data/nodes.json` 和 `edges.json`，注意：

1. 节点 `id` 必须遵循 `{层}_{类型}_{code}` 格式
2. 关系的 `source` 和 `target` 必须指向已存在的节点 id
3. `edge id` 不能重复
4. 修改后 commit + push 即可自动部署

### 方式 C：后端 API（待开发）

架构计划中已设计 FastAPI + Neo4j 后端，支持在页面上直接 CRUD 操作。

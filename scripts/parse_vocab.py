#!/usr/bin/env python3
"""Parse vocabulary markdown files and generate JSON data for the frontend."""
import json
import os
import re
import uuid

BASE = "/Users/sunzhuoqi/Desktop/护肤知识图谱"
OUT = "/Users/sunzhuoqi/Desktop/skincare-kg-platform/frontend/src/data"

nodes = []
edges = []
node_ids = {}  # code -> id mapping
edge_counter = [0]

def make_id(layer, etype, code):
    key = f"{layer}_{etype}_{code}"
    if key not in node_ids:
        node_ids[key] = key
    return key

def add_node(layer, etype, code, label, labelEn="", **props):
    nid = make_id(layer, etype, code)
    nodes.append({
        "id": nid,
        "data": {
            "label": label,
            "labelEn": labelEn,
            "layer": layer,
            "entityType": etype,
            "properties": {"code": code, **{k: v for k, v in props.items() if v}}
        }
    })
    return nid

def add_edge(src, tgt, relType, category, label, **props):
    edge_counter[0] += 1
    edges.append({
        "id": f"edge_{edge_counter[0]:04d}",
        "source": src,
        "target": tgt,
        "data": {
            "relType": relType,
            "category": category,
            "label": label,
            "properties": {k: v for k, v in props.items() if v}
        }
    })

# ============ L2: Ingredients ============
ingredients = {
    # Anti-aging
    "retinol": ("A醇/视黄醇", "Retinol", "caution", "抗老、淡纹、促进代谢", ["A醇", "视黄醇"]),
    "retinal": ("A醛/视黄醛", "Retinal", "caution", "抗老（比A醇强）", ["A醛", "视黄醛"]),
    "hpr": ("HPR", "HPR", "mild_caution", "温和抗老", ["HPR"]),
    "peptide": ("多肽", "Peptide", "safe", "抗老、紧致", ["多肽", "胜肽"]),
    "hexapeptide": ("六胜肽", "Acetyl Hexapeptide", "safe", "淡化表情纹", ["六胜肽"]),
    "collagen": ("胶原蛋白", "Collagen", "safe", "抗老、紧致", ["胶原蛋白"]),
    "bosein": ("玻色因", "Pro-Xylane", "safe", "抗老、紧致", ["玻色因", "波色因"]),
    "resveratrol": ("白藜芦醇", "Resveratrol", "safe", "抗氧化、抗老", []),
    "coq10": ("辅酶Q10", "Coenzyme Q10", "safe", "抗氧化、抗老", ["CoQ10"]),
    "astaxanthin": ("虾青素", "Astaxanthin", "safe", "超强抗氧化", ["虾青素"]),
    "ergothioneine": ("麦角硫因", "Ergothioneine", "safe", "抗氧化", ["麦角硫因"]),
    # Brightening
    "vitamin_c": ("维C/抗坏血酸", "Ascorbic Acid", "mild_caution", "美白、抗氧化", ["VC", "维C"]),
    "niacinamide": ("烟酰胺", "Niacinamide", "safe", "美白、控油、缩毛孔", ["烟酰胺", "VB3"]),
    "arbutin": ("熊果苷", "Arbutin", "safe", "美白", ["熊果苷"]),
    "tranexamic_acid": ("传明酸", "Tranexamic Acid", "safe", "美白、淡斑", ["传明酸", "氨甲环酸"]),
    "glabridin": ("光甘草定", "Glabridin", "safe", "美白", ["光甘草定"]),
    "azelaic_acid": ("壬二酸", "Azelaic Acid", "mild_caution", "美白、祛痘", ["壬二酸"]),
    "kojic_acid": ("曲酸", "Kojic Acid", "mild_caution", "美白淡斑", ["曲酸"]),
    "pitera": ("PITERA", "Pitera", "safe", "调节代谢、提亮", ["PITERA"]),
    # Hydrating
    "hyaluronic_acid": ("玻尿酸", "Hyaluronic Acid", "safe", "补水保湿", ["玻尿酸", "透明质酸"]),
    "ceramide": ("神经酰胺", "Ceramide", "safe", "屏障修护、保湿", ["神经酰胺"]),
    "squalane": ("角鲨烷", "Squalane", "safe", "保湿、修护", ["角鲨烷"]),
    "panthenol": ("泛醇/维B5", "Panthenol", "safe", "修护、保湿、舒缓", ["泛醇", "VB5", "B5"]),
    "allantoin": ("尿囊素", "Allantoin", "safe", "修护、舒缓", ["尿囊素"]),
    "ectoin": ("依克多因", "Ectoin", "safe", "保湿、抗炎", ["依克多因"]),
    "bifida_ferment": ("二裂酵母", "Bifida Ferment Lysate", "safe", "修护、抗老", ["二裂酵母"]),
    "madecassoside": ("羟基积雪草苷", "Madecassoside", "safe", "修护、舒缓", ["积雪草精华"]),
    "glycerin": ("甘油", "Glycerin", "safe", "保湿", ["甘油"]),
    "beta_glucan": ("β-葡聚糖", "Beta-Glucan", "safe", "修护、舒缓", ["葡聚糖"]),
    "reishi": ("灵芝提取物", "Ganoderma Extract", "safe", "修护、维稳", ["灵芝"]),
    # Oil control
    "salicylic_acid": ("水杨酸", "Salicylic Acid", "caution", "控油、祛痘", ["水杨酸", "BHA"]),
    "aha": ("果酸", "Alpha Hydroxy Acid", "caution", "去角质、控油", ["果酸", "AHA"]),
    "glycolic_acid": ("甘醇酸", "Glycolic Acid", "caution", "去角质", ["甘醇酸"]),
    "mandelic_acid": ("杏仁酸", "Mandelic Acid", "mild_caution", "温和去角质", ["杏仁酸"]),
    "tea_tree": ("茶树精油", "Tea Tree Oil", "mild_caution", "抗菌祛痘", ["茶树"]),
    "zinc_pca": ("PCA锌", "Zinc PCA", "safe", "控油、抗菌", ["PCA锌"]),
    # Soothing
    "centella": ("积雪草", "Centella Asiatica", "safe", "修护、舒缓抗炎", ["积雪草", "CICA"]),
    "licorice_root": ("甘草酸二钾", "Dipotassium Glycyrrhizate", "safe", "舒缓、抗炎", ["甘草"]),
    "chamomile": ("洋甘菊", "Chamomile", "safe", "舒缓、抗敏", ["洋甘菊"]),
    "aloe": ("芦荟", "Aloe Vera", "safe", "舒缓、保湿", ["芦荟"]),
    "calendula": ("金盏花", "Calendula", "safe", "舒缓、修护", ["金盏花"]),
    # Sunscreen
    "zinc_oxide": ("氧化锌", "Zinc Oxide", "safe", "物理防晒", []),
    "titanium_dioxide": ("二氧化钛", "Titanium Dioxide", "safe", "物理防晒", []),
    # Controversial
    "alcohol": ("酒精", "Alcohol", "mild_caution", "促渗透", ["酒精"]),
    "fragrance": ("香精", "Fragrance", "mild_caution", "调香", ["香精"]),
}

for code, (label, en, risk, efficacy, aliases) in ingredients.items():
    add_node("L2", "Ingredient", code, label, en, riskLevel=risk, efficacy=efficacy, aliases=aliases)

# ============ L2: Efficacy labels ============
efficacies = [
    ("hydrating", "补水"), ("moisturizing", "保湿锁水"), ("barrier_repair", "屏障修护"),
    ("oil_control", "控油"), ("pore_refining", "收毛孔"), ("anti_wrinkle", "抗皱淡纹"),
    ("firming_lifting", "紧致提拉"), ("brightening", "提亮美白"), ("spot_fading", "淡斑"),
    ("soothing", "舒缓镇静"), ("anti_acne", "祛痘"), ("acne_mark_fading", "淡痘印"),
    ("anti_oxidant", "抗氧化"), ("exfoliating", "去角质"), ("anti_inflammatory", "抗炎"),
    ("cell_renewal", "促进代谢"), ("collagen_boost", "促进胶原生成"),
    ("sun_protection", "防晒"), ("water_oil_balance", "水油平衡"),
]
for code, label in efficacies:
    add_node("L2", "Efficacy", code, label)

# ============ L2: has_efficacy edges (from matrix) ============
efficacy_map = {
    "hyaluronic_acid": ["hydrating", "moisturizing"],
    "ceramide": ["moisturizing", "barrier_repair", "soothing"],
    "panthenol": ["moisturizing", "barrier_repair", "soothing"],
    "ectoin": ["moisturizing", "barrier_repair", "soothing", "anti_oxidant"],
    "retinol": ["anti_wrinkle", "firming_lifting", "brightening"],
    "retinal": ["anti_wrinkle", "firming_lifting"],
    "peptide": ["anti_wrinkle", "firming_lifting"],
    "bosein": ["anti_wrinkle", "firming_lifting"],
    "vitamin_c": ["brightening", "spot_fading", "anti_oxidant"],
    "niacinamide": ["brightening", "oil_control", "pore_refining"],
    "arbutin": ["brightening", "spot_fading"],
    "tranexamic_acid": ["brightening", "spot_fading"],
    "glabridin": ["brightening", "spot_fading"],
    "salicylic_acid": ["oil_control", "pore_refining", "anti_acne", "exfoliating"],
    "aha": ["oil_control", "exfoliating"],
    "astaxanthin": ["anti_oxidant"],
    "ergothioneine": ["anti_oxidant"],
    "resveratrol": ["anti_oxidant", "anti_wrinkle"],
    "centella": ["barrier_repair", "soothing"],
    "bifida_ferment": ["barrier_repair", "anti_oxidant"],
    "tea_tree": ["anti_acne"],
    "glycerin": ["hydrating"],
    "reishi": ["barrier_repair", "soothing"],
    "squalane": ["moisturizing"],
    "azelaic_acid": ["spot_fading", "anti_acne"],
    "mandelic_acid": ["exfoliating"],
    "zinc_pca": ["oil_control"],
    "collagen": ["firming_lifting"],
    "aloe": ["soothing", "hydrating"],
    "licorice_root": ["soothing", "anti_inflammatory"],
    "allantoin": ["barrier_repair", "soothing"],
}
for ing_code, eff_codes in efficacy_map.items():
    for eff_code in eff_codes:
        src = make_id("L2", "Ingredient", ing_code)
        tgt = make_id("L2", "Efficacy", eff_code)
        add_edge(src, tgt, "has_efficacy", "因果归因", "功效")

# ============ L2: conflicts_with ============
conflicts = [
    ("retinol", "aha", "需间隔使用", "12h+", "同时用刺激过大，可能损伤屏障"),
    ("retinol", "salicylic_acid", "需间隔使用", "12h+", "叠加去角质过度"),
    ("retinol", "vitamin_c", "需间隔使用", "12h+", "pH冲突，降低稳定性"),
    ("vitamin_c", "niacinamide", "降低效果", "10min+", "pH差异可能影响效果"),
    ("aha", "salicylic_acid", "不可同时使用", "", "叠加去角质过度"),
]
for a, b, ctype, interval, note in conflicts:
    src = make_id("L2", "Ingredient", a)
    tgt = make_id("L2", "Ingredient", b)
    add_edge(src, tgt, "conflicts_with", "互斥约束", "冲突", constraint_type=ctype, interval=interval, note=note)

# ============ L2: synergizes_with ============
synergies = [
    ("vitamin_c", "resveratrol", "协同抗氧化"),
    ("retinol", "peptide", "肽可缓解A醇刺激"),
    ("retinol", "ceramide", "神经酰胺帮助修护屏障"),
    ("niacinamide", "hyaluronic_acid", "控油+补水经典搭配"),
    ("niacinamide", "tranexamic_acid", "多通路美白"),
    ("salicylic_acid", "niacinamide", "BHA清洁+烟酰胺修护"),
    ("centella", "panthenol", "协同修护"),
    ("ceramide", "panthenol", "修护屏障经典组合"),
    ("hyaluronic_acid", "ceramide", "先补水再锁水"),
    ("ectoin", "centella", "协同抗炎修护"),
    ("astaxanthin", "ergothioneine", "双抗核心配方"),
]
for a, b, note in synergies:
    src = make_id("L2", "Ingredient", a)
    tgt = make_id("L2", "Ingredient", b)
    add_edge(src, tgt, "synergizes_with", "协同增强", "协同", note=note)

# ============ L2: risk_for ============
risks = [
    ("retinol", "sensitive", "刺激、泛红", "初次使用/高浓度"),
    ("retinol", "pregnant", "致畸风险", "孕期禁用"),
    ("aha", "sensitive", "刺激", "高浓度/角质薄"),
    ("salicylic_acid", "sensitive", "刺激", "敏感期不宜"),
    ("vitamin_c", "sensitive", "刺激、泛红", "高浓度/pH低"),
    ("niacinamide", "sensitive", "泛红", "浓度>5%"),
    ("alcohol", "sensitive", "刺激", "高浓度"),
    ("fragrance", "sensitive", "过敏", "累积性致敏"),
]
# Add skin type nodes for risk targets
for code, label in [("sensitive", "敏感肌"), ("pregnant", "孕妇"), ("oily", "油性肌"), ("acne_prone", "痘痘肌")]:
    add_node("L0", "SkinType", code, label)

for ing, skin, risktype, condition in risks:
    src = make_id("L2", "Ingredient", ing)
    tgt = make_id("L0", "SkinType", skin)
    add_edge(src, tgt, "risk_for", "互斥约束", "风险", constraint_type=risktype, condition=condition)

# ============ L2: requires_tolerance ============
tolerances = [
    ("retinol", "4-8周", "从0.1%起步，三明治法"),
    ("aha", "2-4周", "从5%起步→8%→10%"),
    ("salicylic_acid", "1-2周", "从0.5%→1%→2%"),
    ("vitamin_c", "2-4周", "从5%→10%→15%→20%"),
    ("niacinamide", "1-2周", "从2%→5%→10%"),
]
for code, interval, note in tolerances:
    src = make_id("L2", "Ingredient", code)
    add_edge(src, src, "requires_tolerance", "互斥约束", "耐受", interval=interval, note=note, constraint_type="需耐受")

# ============ L2: Symptoms ============
symptoms = [
    ("redness", "泛红", "repair.sensitive_soothe"),
    ("flaking", "脱皮", "hydration.basic_hydration"),
    ("oiliness", "出油", "oil_control.sebum_control"),
    ("fine_lines", "细纹", "anti_aging.fine_lines"),
    ("dullness", "暗沉", "brightening.dullness"),
    ("acne_active", "活痘", "acne.active_acne"),
    ("comedone", "闭口/粉刺", "acne.blackhead_comedone"),
    ("stinging", "刺痛", "repair.sensitive_soothe"),
    ("roughness", "粗糙", "hydration"),
    ("dark_circles", "黑眼圈", "anti_aging.eye_aging"),
    ("sunburn", "晒伤", "repair.sun_damage_repair"),
]
for code, label, concern in symptoms:
    add_node("L2", "Symptom", code, label, concern=concern)

# ============ L2: Adverse Reactions ============
reactions = [
    ("allergy", "过敏反应", "moderate-severe"),
    ("breakout", "闷痘/爆痘", "mild-moderate"),
    ("purging", "清洁反应", "mild"),
    ("over_exfoliation", "过度去角质", "moderate-severe"),
    ("pilling", "搓泥", "mild"),
]
for code, label, severity in reactions:
    add_node("L2", "AdverseReaction", code, label, severity=severity)

# ============ L1: Brands ============
brands = [
    # International luxury
    ("la_mer", "海蓝之谜", "La Mer", "international_luxury"),
    ("estee_lauder", "雅诗兰黛", "Estée Lauder", "international_luxury"),
    ("sk_ii", "SK-II", "SK-II", "international_luxury"),
    ("helena", "赫莲娜", "Helena Rubinstein", "international_luxury"),
    ("la_prairie", "莱珀妮", "La Prairie", "international_luxury"),
    # International mid
    ("lancome", "兰蔻", "Lancôme", "international_mid"),
    ("kiehls", "科颜氏", "Kiehl's", "international_mid"),
    ("clarins", "娇韵诗", "Clarins", "international_mid"),
    ("shiseido", "资生堂", "Shiseido", "international_mid"),
    ("clinique", "倩碧", "Clinique", "international_mid"),
    ("fresh", "Fresh", "Fresh", "international_mid"),
    ("curel", "珂润", "Curél", "international_mid"),
    ("decorte", "黛珂", "Decorté", "international_mid"),
    # International affordable
    ("loreal", "欧莱雅", "L'Oréal", "international_affordable"),
    ("cerave", "CeraVe", "CeraVe", "international_affordable"),
    ("the_ordinary", "The Ordinary", "The Ordinary", "international_affordable"),
    # Domestic premium
    ("proya", "珀莱雅", "PROYA", "domestic_premium"),
    ("winona", "薇诺娜", "Winona", "domestic_premium"),
    ("uniskin", "优时颜", "UNISKIN", "domestic_premium"),
    ("zhuben", "逐本", "ZHUBEN", "domestic_premium"),
    ("quadha", "夸迪", "QUADHA", "domestic_premium"),
    # Functional
    ("skinceuticals", "修丽可", "SkinCeuticals", "functional"),
    ("lrp", "理肤泉", "La Roche-Posay", "functional"),
    ("avene", "雅漾", "Avène", "functional"),
    ("dryu", "玉泽", "Dr.Yu", "functional"),
    ("comfy", "可复美", "Comfy", "functional"),
    ("betterderm", "博乐达", "BetterDerm", "functional"),
]
for code, label, en, tier in brands:
    add_node("L1", "Brand", code, label, en, tier=tier)

# ============ L1: SKUs (popular products) ============
skus = [
    ("little_black", "小黑瓶肌底精华", "lancome", "精华", ["小黑瓶"], "bifida_ferment"),
    ("little_brown", "特润修护精华", "estee_lauder", "精华", ["小棕瓶"], "bifida_ferment"),
    ("fairy_water", "护肤精华露", "sk_ii", "精华水", ["神仙水"], "pitera"),
    ("double_serum", "双萃精华", "clarins", "精华", ["双萃"], ""),
    ("red_waist", "红妍肌活精华", "shiseido", "精华", ["红腰子"], "reishi"),
    ("double_anti", "双抗精华", "proya", "精华", ["双抗"], "astaxanthin,ergothioneine"),
    ("ruby", "红宝石精华", "proya", "精华", ["红宝石"], "retinol,hexapeptide"),
    ("ce_serum", "CE抗氧精华", "skinceuticals", "精华", ["CE精华"], "vitamin_c"),
    ("b5_serum", "B5修护精华", "skinceuticals", "精华", ["B5精华"], "panthenol,hyaluronic_acid"),
    ("purple_iron", "紫铁精华", "kiehls", "精华", ["紫铁"], "retinol"),
    ("moisture_cream", "保湿面霜", "cerave", "面霜", ["保湿霜"], "ceramide"),
    ("special_cream", "特护霜", "winona", "面霜", ["特护霜"], "madecassoside"),
    ("barrier_cream", "屏障修护霜", "dryu", "面霜", ["屏障霜"], "ceramide"),
]
for code, label, brand, category, aliases, key_ing in skus:
    nid = add_node("L1", "SKU", code, label, brand=brand, category=category, aliases=aliases, keyIngredients=key_ing)
    # contains edge: SKU → Brand
    brand_id = make_id("L1", "Brand", brand)
    add_edge(nid, brand_id, "contains", "组成归属", "含有")
    # contains edge: SKU → key ingredients
    if key_ing:
        for ing in key_ing.split(","):
            ing = ing.strip()
            if ing:
                ing_id = make_id("L2", "Ingredient", ing)
                add_edge(nid, ing_id, "contains", "组成归属", "含有")

# ============ L3: Skincare Plans ============
plans = [
    ("dry_sensitive_basic", "干敏肌基础修护方案", ["cleanser", "toner", "ceramide_serum", "barrier_cream", "sunscreen"], "dry,sensitive", "repair"),
    ("oily_acne_control", "油痘肌控油方案", ["cleanser", "salicylic_toner", "niacinamide_serum", "light_moisturizer", "sunscreen"], "oily,acne_prone", "oil_control"),
    ("anti_aging_basic", "初抗老方案", ["cleanser", "toner", "vc_serum_am", "retinol_serum_pm", "eye_cream", "moisturizer", "sunscreen"], "normal,combination", "anti_aging"),
    ("brightening", "美白提亮方案", ["cleanser", "vc_toner", "niacinamide_serum", "arbutin_serum", "moisturizer", "sunscreen"], "all", "brightening"),
]
for code, label, steps, skin, concern in plans:
    add_node("L3", "SkincarePlan", code, label, steps=steps, suitableSkin=skin, targetConcern=concern)

# ============ L5: Synonym Mappings (sample) ============
synonyms = [
    ("retinol_syn", "A醇", ["A醇", "视黄醇", "早C晚A的A", "retinol"], "retinol"),
    ("vc_syn", "维C", ["VC", "维C", "维生素C", "抗坏血酸", "早C晚A的C"], "vitamin_c"),
    ("nia_syn", "烟酰胺", ["烟酰胺", "VB3", "维生素B3", "niacinamide"], "niacinamide"),
    ("ha_syn", "玻尿酸", ["玻尿酸", "透明质酸", "HA", "hyaluronic"], "hyaluronic_acid"),
    ("cer_syn", "神经酰胺", ["神经酰胺", "ceramide", "赛洛美"], "ceramide"),
    ("bha_syn", "水杨酸", ["水杨酸", "BHA", "salicylic"], "salicylic_acid"),
    ("aha_syn", "果酸", ["果酸", "AHA", "刷酸", "glycolic"], "aha"),
    ("cica_syn", "积雪草", ["积雪草", "CICA", "老虎草", "centella"], "centella"),
    ("bosein_syn", "玻色因", ["玻色因", "波色因", "pro-xylane", "ProXylane"], "bosein"),
    ("little_black_syn", "小黑瓶", ["小黑瓶", "兰蔻精华", "黑瓶"], "little_black"),
    ("fairy_water_syn", "神仙水", ["神仙水", "SKII精华", "护肤精华露"], "fairy_water"),
    ("double_anti_syn", "双抗", ["双抗", "珀莱雅双抗", "双抗精华"], "double_anti"),
    ("sensitive_syn", "敏感肌", ["敏感肌", "敏感皮", "敏皮", "红血丝"], "sensitive"),
    ("dry_syn", "干皮", ["干皮", "干性肌肤", "干性皮肤", "大干皮"], "dry"),
    ("oily_syn", "油皮", ["油皮", "油性肌肤", "大油田", "爱出油"], "oily"),
]
for code, canonical, variants, target in synonyms:
    nid = add_node("L5", "SynonymMapping", code, canonical, canonical=canonical, variants=variants, target=target)
    # maps_to edge
    # Try to find the target node
    possible_targets = [
        make_id("L2", "Ingredient", target),
        make_id("L1", "SKU", target),
        make_id("L0", "SkinType", target),
    ]
    for tid in possible_targets:
        if tid in node_ids:
            add_edge(nid, tid, "maps_to", "等价映射", "映射")
            break

# ============ L4: Intents (sample) ============
intents = [
    ("seek_recommendation", "求推荐", "skincare", 1),
    ("product_inquiry", "产品咨询", "skincare", 2),
    ("ingredient_query", "成分咨询", "skincare", 3),
    ("skin_concern", "肤质问题", "skincare", 4),
    ("aftersales", "售后问题", "aftersales", 1),
    ("promo_inquiry", "大促咨询", "promotion", 1),
    ("makeup_how", "妆教咨询", "makeup", 1),
]
for code, label, channel, priority in intents:
    add_node("L4", "Intent", code, label, channel=channel, priority=priority)

# ============ L0: Additional profile nodes ============
for code, label in [("dry", "干性"), ("oily", "油性"), ("combination", "混合"), ("normal", "中性")]:
    if make_id("L0", "SkinType", code) not in node_ids:
        add_node("L0", "SkinType", code, label)

concerns = [
    ("hydration", "保湿补水"), ("oil_control", "控油"), ("anti_aging", "抗老"),
    ("brightening", "美白提亮"), ("acne", "祛痘"), ("repair", "修护"),
]
for code, label in concerns:
    add_node("L0", "Concern", code, label)

budgets = [
    ("ultra_budget", "极低预算 (<100)"), ("budget", "低预算 (100-200)"),
    ("affordable", "平价 (200-400)"), ("mid_range", "中等 (400-800)"),
    ("premium", "高端 (800-1500)"), ("luxury", "奢华 (1500+)"),
]
for code, label in budgets:
    add_node("L0", "Budget", code, label)

# ============ Write output ============
os.makedirs(OUT, exist_ok=True)
with open(os.path.join(OUT, "nodes.json"), "w", encoding="utf-8") as f:
    json.dump(nodes, f, ensure_ascii=False, indent=2)
with open(os.path.join(OUT, "edges.json"), "w", encoding="utf-8") as f:
    json.dump(edges, f, ensure_ascii=False, indent=2)

print(f"Generated {len(nodes)} nodes and {len(edges)} edges")
print(f"Output: {OUT}/nodes.json, {OUT}/edges.json")

#!/usr/bin/env python3
"""
Parse vocabulary markdown files and generate JSON data for the frontend.
Covers all 6 layers (L0~L5) from the original vocabulary documents.
"""
import json
import os

BASE = "/Users/sunzhuoqi/Desktop/护肤知识图谱"
OUT = "/Users/sunzhuoqi/Desktop/skincare-kg-platform/frontend/src/data"

nodes = []
edges = []
node_ids = {}  # id -> True
edge_counter = [0]


def make_id(layer, etype, code):
    key = f"{layer}_{etype}_{code}"
    return key


def add_node(layer, etype, code, label, labelEn="", **props):
    nid = make_id(layer, etype, code)
    if nid in node_ids:
        return nid  # skip duplicate
    node_ids[nid] = True
    nodes.append({
        "id": nid,
        "data": {
            "label": label,
            "labelEn": labelEn,
            "layer": layer,
            "entityType": etype,
            "properties": {"code": code, **{k: v for k, v in props.items() if v is not None and v != ""}}
        }
    })
    return nid


def add_edge(src, tgt, relType, category, label, **props):
    if src not in node_ids or tgt not in node_ids:
        return  # skip edges with missing nodes
    edge_counter[0] += 1
    edges.append({
        "id": f"edge_{edge_counter[0]:04d}",
        "source": src,
        "target": tgt,
        "data": {
            "relType": relType,
            "category": category,
            "label": label,
            "properties": {k: v for k, v in props.items() if v is not None and v != ""}
        }
    })


# ================================================================
# L0: 用户画像层
# ================================================================

# --- 1. Skin Types (base) ---
skin_types = [
    ("dry", "干皮", "Dry"),
    ("oily", "油皮", "Oily"),
    ("combination", "混合肌", "Combination"),
    ("combination_oily", "混合偏油", "Combination Oily"),
    ("combination_dry", "混合偏干", "Combination Dry"),
    ("sensitive", "敏感肌", "Sensitive"),
    ("neutral", "中性肌", "Neutral"),
]
for code, label, en in skin_types:
    add_node("L0", "SkinType", code, label, en)

# Skin type modifiers
skin_modifiers = [
    ("mod_sensitive", "敏感特征"),
    ("mod_acne_prone", "易痘特征"),
    ("mod_mature", "熟龄特征"),
    ("mod_dehydrated", "外油内干"),
    ("mod_tolerant", "耐受/城墙皮"),
    ("mod_pigmented", "易色沉"),
]
for code, label in skin_modifiers:
    add_node("L0", "SkinType", code, label)

# Additional risk target skin types
for code, label in [("pregnant", "孕妇"), ("acne_prone", "痘痘肌")]:
    add_node("L0", "SkinType", code, label)

# --- 2. Concerns (10 categories with sub-concerns) ---
concerns_full = [
    # hydration
    ("hydration", "补水保湿"),
    ("hydration_basic", "基础补水"),
    ("hydration_deep", "深层滋养"),
    ("hydration_barrier", "屏障修护"),
    ("hydration_balance", "水油平衡"),
    # oil_control
    ("oil_control", "控油"),
    ("oil_control_sebum", "控油脂"),
    ("oil_control_pore", "毛孔管理"),
    ("oil_control_shine", "控光泽"),
    # anti_aging
    ("anti_aging", "抗老"),
    ("anti_aging_lines", "淡纹"),
    ("anti_aging_firming", "紧致"),
    ("anti_aging_early", "初老预防"),
    ("anti_aging_neck", "颈部抗老"),
    ("anti_aging_eye", "眼周抗老"),
    # repair
    ("repair", "修护"),
    ("repair_sensitive", "敏感舒缓"),
    ("repair_post_procedure", "医美后修护"),
    ("repair_season", "换季维稳"),
    ("repair_sun_damage", "晒后修护"),
    ("repair_over_exfoliation", "过度去角质修护"),
    # brightening
    ("brightening", "美白提亮"),
    ("brightening_whitening", "美白"),
    ("brightening_dullness", "改善暗沉"),
    ("brightening_glow", "提亮光泽"),
    ("brightening_spot", "淡斑"),
    ("brightening_even_tone", "匀肤色"),
    # acne
    ("acne", "战痘"),
    ("acne_active", "活痘治疗"),
    ("acne_scar", "痘印淡化"),
    ("acne_blackhead", "黑头闭口"),
    ("acne_hormonal", "激素痘"),
    ("acne_body", "身体痘"),
    # makeup_fit
    ("makeup_fit", "底妆适配"),
    ("makeup_fit_cakey", "防卡粉"),
    ("makeup_fit_lasting", "持妆"),
    ("makeup_fit_coverage", "遮瑕"),
    ("makeup_fit_natural", "自然妆感"),
    ("makeup_fit_oil_control", "底妆控油"),
    # cleansing
    ("cleansing", "清洁"),
    ("cleansing_deep", "深层清洁"),
    ("cleansing_gentle", "温和洁面"),
    ("cleansing_makeup_removal", "卸妆"),
    # sun_protection
    ("sun_protection", "防晒"),
    ("sun_daily", "日常防晒"),
    ("sun_outdoor", "户外防晒"),
    ("sun_texture", "防晒肤感"),
    ("sun_reapply", "补涂"),
    # body_care
    ("body_care", "身体护理"),
    ("body_moisturize", "身体保湿"),
    ("body_whitening", "身体美白"),
    ("body_hand", "手部护理"),
    ("body_lip", "唇部护理"),
]
for code, label in concerns_full:
    add_node("L0", "Concern", code, label)

# --- 3. Age Segments ---
age_segments = [
    ("teen", "15-18 高中生"),
    ("student", "18-22 大学生"),
    ("early_career", "22-26 职场新人"),
    ("young_professional", "26-30 白领"),
    ("early_mature", "30-35 轻熟肌"),
    ("mature", "35-45 熟龄"),
    ("advanced_mature", "45+ 成熟肌"),
]
for code, label in age_segments:
    add_node("L0", "Budget", code + "_age", label)  # use Budget type for enum values

# --- 4. Budget Ranges ---
budgets = [
    ("ultra_budget", "极低预算 (≤100)"),
    ("budget", "低预算 (100-300)"),
    ("affordable", "平价 (200-600)"),
    ("mid_range", "中等 (400-1000)"),
    ("premium", "高端 (800-1500)"),
    ("luxury", "奢华 (1200+)"),
]
for code, label in budgets:
    add_node("L0", "Budget", code, label)

# --- 5. Product Categories ---
product_categories = [
    # Skincare
    ("cleanser", "洁面"), ("makeup_remover", "卸妆"), ("toner", "化妆水"),
    ("lotion", "乳液"), ("lotion_set", "水乳套组"), ("essence", "精华"),
    ("ampoule", "安瓶/次抛"), ("cream", "面霜"), ("eye_cream", "眼霜"),
    ("mask", "面膜"), ("clay_mask", "清洁面膜"), ("sunscreen", "防晒"),
    ("lip_care", "唇部护理"), ("neck_cream", "颈霜"), ("exfoliant", "去角质"),
    ("mist", "喷雾"), ("beauty_device", "美容仪"),
    # Base makeup
    ("base_makeup", "粉底"), ("cushion", "气垫"), ("bb_cc", "BB/CC霜"),
    ("primer", "妆前乳"), ("concealer", "遮瑕"), ("setting_powder", "定妆粉"),
    ("setting_spray", "定妆喷雾"),
    # Body care
    ("body_lotion", "身体乳"), ("body_sunscreen", "身体防晒"),
    ("hand_cream", "护手霜"), ("body_scrub", "身体磨砂"), ("body_wash", "沐浴"),
    # Cross-category
    ("comprehensive", "综合护肤方案"), ("full_routine", "全套流程"),
]
for code, label in product_categories:
    add_node("L0", "Concern", "cat_" + code, label)

# --- 6. Usage Scenarios ---
scenarios = [
    # Environment
    ("seasonal_change", "换季"), ("summer_hot", "夏天闷热"),
    ("winter_dry", "冬天干燥"), ("office_ac", "空调房"),
    ("outdoor_active", "户外运动"), ("travel_business", "出差旅行"),
    ("high_altitude", "高原强紫外"),
    # Life
    ("overtime_fatigue", "熬夜加班"), ("student_life", "学生生活"),
    ("daily_makeup", "日常带妆"), ("pre_event", "重要场合"),
    ("pregnancy", "孕期"), ("menstrual", "经期"),
    ("post_medical", "医美后"), ("wedding_prep", "备婚"),
    # Shopping
    ("promotion_shopping", "大促购物"), ("first_purchase", "首次购买"),
    ("repurchase", "回购"), ("gift_buying", "送礼"), ("trial_sample", "试用"),
]
for code, label in scenarios:
    add_node("L0", "Concern", "sce_" + code, label)

# --- 7. Conversation Contexts ---
conv_contexts = [
    ("ctx_promotion", "大促购物场景"),
    ("ctx_learning", "学习咨询场景"),
    ("ctx_urgent", "急需解决场景"),
    ("ctx_routine", "日常换品场景"),
    ("ctx_aftersales", "售后问题场景"),
    ("ctx_casual", "闲聊场景"),
]
for code, label in conv_contexts:
    add_node("L0", "Concern", code, label)

# --- 8. Skin Concerns/Risks ---
risk_concerns = [
    ("fear_breakout", "怕闷痘"), ("fear_irritation", "怕刺激"),
    ("fear_greasy", "怕油腻"), ("fear_pilling", "怕搓泥"),
    ("fear_photosensitive", "怕光敏"), ("fear_dependency", "怕依赖"),
    ("fear_purging", "怕爆痘"), ("fear_interaction", "怕冲突"),
]
for code, label in risk_concerns:
    add_node("L0", "Concern", code, label)

# ================================================================
# L1: 商品层
# ================================================================

# --- Brands (all 88 brands from 6 tiers) ---
brands = [
    # international_luxury (10)
    ("la_mer", "海蓝之谜", "La Mer", "international_luxury"),
    ("estee_lauder", "雅诗兰黛", "Estée Lauder", "international_luxury"),
    ("cpb", "CPB肌肤之钥", "Clé de Peau Beauté", "international_luxury"),
    ("helena", "赫莲娜", "Helena Rubinstein", "international_luxury"),
    ("sk_ii", "SK-II", "SK-II", "international_luxury"),
    ("la_prairie", "莱珀妮", "La Prairie", "international_luxury"),
    ("sisley", "希思黎", "Sisley", "international_luxury"),
    ("philosophy", "肌肤哲理", "Philosophy", "international_luxury"),
    ("decorte_aq", "黛珂AQ线", "Decorté AQ", "international_luxury"),
    ("erno_laszlo", "奥伦纳素", "Erno Laszlo", "international_luxury"),
    # international_mid (15)
    ("lancome", "兰蔻", "Lancôme", "international_mid"),
    ("kiehls", "科颜氏", "Kiehl's", "international_mid"),
    ("clarins", "娇韵诗", "Clarins", "international_mid"),
    ("decorte", "黛珂", "Decorté", "international_mid"),
    ("shiseido", "资生堂", "Shiseido", "international_mid"),
    ("clinique", "倩碧", "Clinique", "international_mid"),
    ("origins", "悦木之源", "Origins", "international_mid"),
    ("elizabeth_arden", "雅顿", "Elizabeth Arden", "international_mid"),
    ("biotherm", "碧欧泉", "Biotherm", "international_mid"),
    ("fresh", "Fresh", "Fresh", "international_mid"),
    ("ipsa", "茵芙莎", "IPSA", "international_mid"),
    ("curel", "珂润", "Curél", "international_mid"),
    ("bobbi_brown", "芭比波朗", "Bobbi Brown", "international_mid"),
    ("nars", "NARS", "NARS", "international_mid"),
    ("mac", "MAC", "MAC", "international_mid"),
    # international_affordable (9)
    ("loreal", "欧莱雅", "L'Oréal", "international_affordable"),
    ("cerave", "CeraVe", "CeraVe", "international_affordable"),
    ("the_ordinary", "The Ordinary", "The Ordinary", "international_affordable"),
    ("nivea", "妮维雅", "NIVEA", "international_affordable"),
    ("mentholatum", "曼秀雷敦", "Mentholatum", "international_affordable"),
    ("neutrogena", "露得清", "Neutrogena", "international_affordable"),
    ("ponds", "旁氏", "Pond's", "international_affordable"),
    ("vaseline", "凡士林", "Vaseline", "international_affordable"),
    ("dove", "多芬", "Dove", "international_affordable"),
    # domestic_premium (12)
    ("proya", "珀莱雅", "PROYA", "domestic_premium"),
    ("winona", "薇诺娜", "Winona", "domestic_premium"),
    ("uniskin", "优时颜", "UNISKIN", "domestic_premium"),
    ("marubi", "丸美", "MARUBI", "domestic_premium"),
    ("timage", "彩棠", "Timage", "domestic_premium"),
    ("florasis", "花西子", "Florasis", "domestic_premium"),
    ("maogeping", "毛戈平", "MAOGEPING", "domestic_premium"),
    ("simpcare", "溪木源", "SIMPCARE", "domestic_premium"),
    ("zhuben", "逐本", "ZHUBEN", "domestic_premium"),
    ("zhiben", "至本", "zhiben", "domestic_premium"),
    ("quadha", "夸迪", "QUADHA", "domestic_premium"),
    ("collgene", "可丽金", "Collgene", "domestic_premium"),
    # domestic_affordable (12)
    ("pechoin", "百雀羚", "Pechoin", "domestic_affordable"),
    ("chando", "自然堂", "CHANDO", "domestic_affordable"),
    ("guyu", "谷雨", "GUYU", "domestic_affordable"),
    ("biohyalux", "润百颜", "BIOHYALUX", "domestic_affordable"),
    ("inoherb", "相宜本草", "INOHERB", "domestic_affordable"),
    ("kans", "韩束", "KANS", "domestic_affordable"),
    ("colorkey", "珂拉琪", "Colorkey", "domestic_affordable"),
    ("perfect_diary", "完美日记", "Perfect Diary", "domestic_affordable"),
    ("judydoll", "橘朵", "Judydoll", "domestic_affordable"),
    ("joocyee", "酵色", "Joocyee", "domestic_affordable"),
    ("banmuhuatian", "半亩花田", "BM", "domestic_affordable"),
    ("kixiran", "肌司研", "KIXIRAN", "domestic_affordable"),
    # functional (12)
    ("skinceuticals", "修丽可", "SkinCeuticals", "functional"),
    ("lrp", "理肤泉", "La Roche-Posay", "functional"),
    ("avene", "雅漾", "Avène", "functional"),
    ("vichy", "薇姿", "Vichy", "functional"),
    ("freeplus", "芙丽芳丝", "Freeplus", "functional"),
    ("comfy", "可复美", "Comfy", "functional"),
    ("prox", "珀肤研", "PROX", "functional"),
    ("dryu", "玉泽", "Dr.Yu", "functional"),
    ("betterderm", "博乐达", "BetterDerm", "functional"),
    ("fuyijia", "敷尔佳", "Fuyijia", "functional"),
    ("biohyalux_med", "润百颜医美线", "BIOHYALUX Med", "functional"),
    ("aiyu", "艾遇", "AIYU", "functional"),
    # Sunscreen brand
    ("anessa", "安热沙", "Anessa", "international_mid"),
    # OLAY
    ("olay", "OLAY", "OLAY", "international_affordable"),
]
for code, label, en, tier in brands:
    add_node("L1", "Brand", code, label, en, tier=tier)

# --- SPU Products (complete from L1 vocabulary) ---
spus = [
    # 2.1 精华类 (19)
    ("little_black", "小黑瓶肌底精华", "lancome", "精华", ["小黑瓶"], "bifida_ferment"),
    ("little_brown", "特润修护精华", "estee_lauder", "精华", ["小棕瓶"], "bifida_ferment"),
    ("double_serum", "双萃精华", "clarins", "精华", ["双萃"], ""),
    ("red_waist", "红妍肌活精华", "shiseido", "精华", ["红腰子"], "reishi"),
    ("fairy_water", "护肤精华露", "sk_ii", "精华水", ["神仙水"], "pitera"),
    ("little_bulb", "小灯泡精华", "sk_ii", "精华", ["小灯泡"], ""),
    ("black_bindage", "黑绷带面霜", "helena", "面霜", ["黑绷带"], "bosein"),
    ("green_bottle", "绿宝瓶精华", "helena", "精华", ["绿宝瓶"], "bosein"),
    ("double_anti", "双抗精华", "proya", "精华", ["双抗"], "astaxanthin,ergothioneine"),
    ("yuanli", "源力精华", "proya", "精华", ["源力"], ""),
    ("ruby", "红宝石精华", "proya", "精华", ["红宝石"], "retinol,hexapeptide"),
    ("early_c_late_a", "早C晚A组合", "proya", "精华", ["早C晚A"], "vitamin_c,retinol"),
    ("small_syringe", "小针管精华", "uniskin", "精华", ["小针管"], "peptide"),
    ("ce_serum", "CE抗氧精华", "skinceuticals", "精华", ["CE精华"], "vitamin_c"),
    ("se_xiu", "色修精华", "skinceuticals", "精华", ["色修"], ""),
    ("b5_serum", "B5修护精华", "skinceuticals", "精华", ["B5精华"], "panthenol,hyaluronic_acid"),
    ("purple_iron", "紫铁精华", "kiehls", "精华", ["紫铁"], "retinol"),
    ("spot_serum", "淡斑精华", "kiehls", "精华", ["淡斑精华"], "vitamin_c"),
    ("small_white", "小白瓶精华", "olay", "精华", ["小白瓶"], "niacinamide"),
    ("light_sculpt", "光塑瓶精华", "olay", "精华", ["光塑瓶"], ""),
    ("black_serum", "黑精华", "loreal", "精华", ["黑精华"], "bosein"),
    ("purple_iron_loreal", "复颜玻尿酸精华", "loreal", "精华", ["紫熨斗精华"], "bosein,hyaluronic_acid"),
    ("quadha_retinol", "夜间修护次抛", "quadha", "精华", ["次抛A醇"], "retinol"),
    # 2.2 面霜类 (12)
    ("guyu_cream", "光感水润面霜", "guyu", "面霜", ["奶罐"], "glabridin"),
    ("black_gravity", "黑引力面霜", "uniskin", "面霜", ["黑引力"], ""),
    ("big_purple", "经典面霜", "kiehls", "面霜", ["大紫瓶"], ""),
    ("collagen_cream", "胶原霜", "estee_lauder", "面霜", ["胶原霜"], "collagen"),
    ("line_cream", "淡纹霜", "estee_lauder", "面霜", ["淡纹霜"], ""),
    ("big_red", "复原蜜面霜", "sk_ii", "面霜", ["大红瓶"], "pitera"),
    ("cream_king", "精华面霜", "la_mer", "面霜", ["面霜之王"], ""),
    ("mushroom_cream", "灵芝面霜", "origins", "面霜", ["灵芝霜"], "reishi"),
    ("cerave_cream", "保湿面霜", "cerave", "面霜", ["保湿霜"], "ceramide"),
    ("special_cream", "特护霜", "winona", "面霜", ["特护霜"], "madecassoside"),
    ("centella_cream", "积雪草面霜", "winona", "面霜", ["积雪草面霜"], "centella"),
    ("barrier_cream", "屏障修护霜", "dryu", "面霜", ["屏障霜"], "ceramide"),
    # 2.3 水乳/套组类 (11)
    ("perilla_water", "紫苏水", "decorte", "化妆水", ["紫苏水"], ""),
    ("avocado_lotion", "牛油果乳液", "decorte", "乳液", ["牛油果乳液"], ""),
    ("aurora_set", "极光甘草水乳", "proya", "水乳", ["极光甘草"], "glabridin"),
    ("yuanli_set", "源力水乳套组", "proya", "水乳", ["源力水乳"], ""),
    ("calendula_water", "金盏花水", "kiehls", "化妆水", ["金盏花水"], "calendula"),
    ("butter_lotion", "经典保湿乳", "clinique", "乳液", ["黄油"], ""),
    ("mushroom_water", "灵芝水", "origins", "化妆水", ["灵芝水"], "reishi"),
    ("health_water", "健康水", "decorte", "化妆水", ["健康水"], ""),
    ("self_discipline", "自律循环水乳", "ipsa", "水乳", ["自律水乳"], ""),
    ("red_waist_set", "红妍水乳", "shiseido", "水乳", ["红腰子水乳"], ""),
    # 2.4 眼霜类 (5)
    ("purple_iron_eye", "紫熨斗眼霜", "loreal", "眼霜", ["紫熨斗"], "bosein"),
    ("red_pen", "弹力蛋白眼霜", "marubi", "眼霜", ["小红笔"], ""),
    ("platinum_eye", "白金眼霜", "la_prairie", "眼霜", ["白金眼霜"], ""),
    ("eye_serum_el", "眼部精华", "estee_lauder", "眼霜", ["小棕瓶眼部"], ""),
    ("green_gem_eye", "绿宝石眼霜", "helena", "眼霜", ["绿宝石眼霜"], "bosein"),
    # 2.5 防晒类 (7)
    ("white_tube", "轻透防晒", "lancome", "防晒", ["小白管"], ""),
    ("gold_bottle", "安热沙金瓶", "anessa", "防晒", ["金瓶防晒", "小金瓶"], ""),
    ("blue_fat", "新艳阳防晒", "shiseido", "防晒", ["蓝胖子"], ""),
    ("big_white", "大白瓶防晒", "loreal", "防晒", ["大白瓶"], ""),
    ("small_milk", "水感防晒", "mentholatum", "防晒", ["小奶瓶"], ""),
    ("soft_light_sun", "柔光防晒", "proya", "防晒", ["柔光防晒"], ""),
    # 2.6 洁面类 (4)
    ("white_mud", "白泥洁面", "kiehls", "洁面", ["白泥"], ""),
    ("amino_cleanser", "氨基酸洁面", "freeplus", "洁面", ["氨基酸洁面"], ""),
    ("cleansing_mousse", "洁面慕斯", "zhiben", "洁面", ["洁面慕斯"], ""),
    ("cleansing_balm", "卸妆膏", "zhuben", "洁面", ["卸妆膏"], ""),
    # 2.7 面膜类 (5)
    ("ex_bf_mask", "急救面膜", "sk_ii", "面膜", ["前男友面膜"], "pitera"),
    ("green_mask", "绿泥面膜", "origins", "面膜", ["绿膜"], ""),
    ("freeze_mask", "冻干面膜", "comfy", "面膜", ["冻干面膜"], ""),
    ("super_a_mask", "超分子水杨酸面膜", "betterderm", "面膜", ["超A面膜"], "salicylic_acid"),
    ("bubble_mask", "泡泡面膜", "fuyijia", "面膜", ["泡泡面膜"], ""),
]
for code, label, brand, category, aliases, key_ing in spus:
    nid = add_node("L1", "SPU", code, label, brand=brand, category=category, aliases=aliases, keyIngredients=key_ing)
    # SPU → Brand edge
    brand_id = make_id("L1", "Brand", brand)
    add_edge(nid, brand_id, "contains", "组成归属", "归属")
    # SPU → Key ingredients edges
    if key_ing:
        for ing in key_ing.split(","):
            ing = ing.strip()
            if ing:
                ing_id = make_id("L2", "Ingredient", ing)
                # Will be connected after L2 nodes are created
                # For now, store for later


# ================================================================
# L2: 知识层
# ================================================================

# --- Ingredients (complete 104+ from all 7 categories) ---
ingredients = {
    # 1.1 Anti-aging (12)
    "retinol": ("A醇/视黄醇", "Retinol", "caution", "抗老、淡纹、促进代谢", ["A醇", "视黄醇"]),
    "retinal": ("A醛/视黄醛", "Retinal", "caution", "抗老（比A醇强）", ["A醛", "视黄醛"]),
    "hpr": ("HPR", "HPR", "mild_caution", "温和抗老", ["HPR"]),
    "peptide": ("多肽", "Peptide", "safe", "抗老、紧致", ["多肽", "胜肽"]),
    "hexapeptide": ("六胜肽", "Acetyl Hexapeptide", "safe", "淡化表情纹", ["六胜肽", "类肉毒素"]),
    "palmitoyl_tripeptide": ("棕榈酰三肽", "Palmitoyl Tripeptide", "safe", "胶原再生", ["三肽"]),
    "collagen": ("胶原蛋白", "Collagen", "safe", "抗老、紧致", ["胶原蛋白", "胶原"]),
    "bosein": ("玻色因", "Pro-Xylane", "safe", "抗老、紧致", ["玻色因", "波色因"]),
    "resveratrol": ("白藜芦醇", "Resveratrol", "safe", "抗氧化、抗老", []),
    "coq10": ("辅酶Q10", "Coenzyme Q10", "safe", "抗氧化、抗老", ["CoQ10"]),
    "astaxanthin": ("虾青素", "Astaxanthin", "safe", "超强抗氧化", ["虾青素"]),
    "ergothioneine": ("麦角硫因", "Ergothioneine", "safe", "抗氧化", ["麦角硫因"]),
    # 1.2 Brightening (8)
    "vitamin_c": ("维C/抗坏血酸", "Ascorbic Acid", "mild_caution", "美白、抗氧化", ["VC", "维C"]),
    "niacinamide": ("烟酰胺", "Niacinamide", "safe", "美白、控油、缩毛孔", ["烟酰胺", "VB3"]),
    "arbutin": ("熊果苷", "Arbutin", "safe", "美白", ["熊果苷", "α-熊果苷"]),
    "tranexamic_acid": ("传明酸", "Tranexamic Acid", "safe", "美白、淡斑", ["传明酸", "氨甲环酸"]),
    "glabridin": ("光甘草定", "Glabridin", "safe", "美白", ["光甘草定"]),
    "azelaic_acid": ("壬二酸", "Azelaic Acid", "mild_caution", "美白、祛痘", ["壬二酸", "杜鹃花酸"]),
    "kojic_acid": ("曲酸", "Kojic Acid", "mild_caution", "美白淡斑", ["曲酸"]),
    "pitera": ("PITERA", "Pitera", "safe", "调节代谢、提亮", ["PITERA"]),
    # 1.3 Hydrating/Repair (12)
    "hyaluronic_acid": ("玻尿酸", "Hyaluronic Acid", "safe", "补水保湿", ["玻尿酸", "透明质酸"]),
    "ceramide": ("神经酰胺", "Ceramide", "safe", "屏障修护、保湿", ["神经酰胺"]),
    "squalane": ("角鲨烷", "Squalane", "safe", "保湿、修护", ["角鲨烷"]),
    "panthenol": ("泛醇/维B5", "Panthenol", "safe", "修护、保湿、舒缓", ["泛醇", "VB5", "B5"]),
    "allantoin": ("尿囊素", "Allantoin", "safe", "修护、舒缓", ["尿囊素"]),
    "ectoin": ("依克多因", "Ectoin", "safe", "保湿、抗炎", ["依克多因"]),
    "bifida_ferment": ("二裂酵母", "Bifida Ferment Lysate", "safe", "修护、抗老", ["二裂酵母"]),
    "madecassoside": ("羟基积雪草苷", "Madecassoside", "safe", "修护、舒缓", ["积雪草精华"]),
    "shea_butter": ("牛油果树果脂", "Shea Butter", "safe", "深层滋润", ["牛油果脂", "乳木果油"]),
    "glycerin": ("甘油", "Glycerin", "safe", "保湿", ["甘油"]),
    "beta_glucan": ("β-葡聚糖", "Beta-Glucan", "safe", "修护、舒缓", ["葡聚糖"]),
    "reishi": ("灵芝提取物", "Ganoderma Extract", "safe", "修护、维稳", ["灵芝"]),
    # 1.4 Oil control/Acne (9)
    "salicylic_acid": ("水杨酸", "Salicylic Acid", "caution", "控油、祛痘", ["水杨酸", "BHA"]),
    "aha": ("果酸", "Alpha Hydroxy Acid", "caution", "去角质、控油", ["果酸", "AHA"]),
    "glycolic_acid": ("甘醇酸", "Glycolic Acid", "caution", "去角质", ["甘醇酸"]),
    "mandelic_acid": ("杏仁酸", "Mandelic Acid", "mild_caution", "温和去角质", ["杏仁酸"]),
    "lha": ("辛酰水杨酸", "Capryloyl Salicylic Acid", "mild_caution", "温和控油疏通", ["LHA"]),
    "pha": ("葡萄糖酸内酯", "Gluconolactone", "safe", "温和去角质、保湿", ["PHA"]),
    "lactobionic_acid": ("乳糖酸", "Lactobionic Acid", "safe", "温和去角质、抗氧化", ["乳糖酸"]),
    "zinc_pca": ("PCA锌", "Zinc PCA", "safe", "控油、抗菌", ["PCA锌"]),
    "tea_tree": ("茶树精油", "Tea Tree Oil", "mild_caution", "抗菌祛痘", ["茶树"]),
    # 1.5 Soothing (6)
    "centella": ("积雪草", "Centella Asiatica", "safe", "修护、舒缓抗炎", ["积雪草", "CICA"]),
    "licorice_root": ("甘草酸二钾", "Dipotassium Glycyrrhizate", "safe", "舒缓、抗炎", ["甘草"]),
    "chamomile": ("洋甘菊", "Chamomile", "safe", "舒缓、抗敏", ["洋甘菊"]),
    "aloe": ("芦荟", "Aloe Vera", "safe", "舒缓、保湿", ["芦荟"]),
    "calendula": ("金盏花", "Calendula", "safe", "舒缓、修护", ["金盏花"]),
    "mugwort": ("艾草", "Mugwort Extract", "safe", "舒缓、抗炎", ["艾草", "艾叶"]),
    # 1.6 Sunscreen (3)
    "zinc_oxide": ("氧化锌", "Zinc Oxide", "safe", "物理防晒", []),
    "titanium_dioxide": ("二氧化钛", "Titanium Dioxide", "safe", "物理防晒", []),
    "chemical_uv_filters": ("化学防晒剂", "Chemical UV Filters", "mild_caution", "化学防晒", ["化学防晒"]),
    # 1.7 Controversial (6)
    "alcohol": ("酒精", "Alcohol", "mild_caution", "促渗透", ["酒精"]),
    "fragrance": ("香精", "Fragrance", "mild_caution", "调香", ["香精"]),
    "essential_oil": ("精油", "Essential Oil", "mild_caution", "芳疗", ["精油"]),
    "mineral_oil": ("矿物油", "Mineral Oil", "safe", "封闭保湿", ["矿物油"]),
    "silicone": ("硅油", "Silicone", "safe", "润滑成膜", ["硅油"]),
    "preservative": ("防腐剂", "Preservative", "safe", "防腐", ["防腐剂"]),
}
for code, (label, en, risk, efficacy, aliases) in ingredients.items():
    add_node("L2", "Ingredient", code, label, en, riskLevel=risk, efficacy=efficacy, aliases=aliases)

# --- Efficacy labels (21) ---
efficacies = [
    ("hydrating", "补水"), ("moisturizing", "保湿锁水"), ("barrier_repair", "屏障修护"),
    ("oil_control", "控油"), ("pore_refining", "收毛孔"), ("anti_wrinkle", "抗皱淡纹"),
    ("firming_lifting", "紧致提拉"), ("brightening", "提亮美白"), ("spot_fading", "淡斑"),
    ("soothing", "舒缓镇静"), ("anti_acne", "祛痘"), ("acne_mark_fading", "淡痘印"),
    ("anti_oxidant", "抗氧化"), ("exfoliating", "去角质"), ("anti_inflammatory", "抗炎"),
    ("cell_renewal", "促进代谢"), ("collagen_boost", "促进胶原生成"),
    ("sun_protection", "防晒"), ("water_oil_balance", "水油平衡"),
    ("makeup_priming", "妆前打底"), ("long_wear", "持妆"),
]
for code, label in efficacies:
    add_node("L2", "Efficacy", code, label)

# --- Ingredient → Efficacy edges (expanded matrix) ---
efficacy_map = {
    "hyaluronic_acid": ["hydrating", "moisturizing"],
    "ceramide": ["moisturizing", "barrier_repair", "soothing"],
    "squalane": ["moisturizing"],
    "panthenol": ["moisturizing", "barrier_repair", "soothing"],
    "ectoin": ["moisturizing", "barrier_repair", "soothing", "anti_oxidant"],
    "allantoin": ["barrier_repair", "soothing"],
    "bifida_ferment": ["barrier_repair", "anti_oxidant"],
    "glycerin": ["hydrating"],
    "reishi": ["barrier_repair", "soothing"],
    "centella": ["barrier_repair", "soothing"],
    "madecassoside": ["barrier_repair", "soothing"],
    "shea_butter": ["moisturizing"],
    "beta_glucan": ["barrier_repair", "soothing"],
    "retinol": ["anti_wrinkle", "firming_lifting", "brightening", "cell_renewal"],
    "retinal": ["anti_wrinkle", "firming_lifting"],
    "hpr": ["anti_wrinkle"],
    "peptide": ["anti_wrinkle", "firming_lifting"],
    "hexapeptide": ["anti_wrinkle"],
    "palmitoyl_tripeptide": ["collagen_boost", "firming_lifting"],
    "bosein": ["anti_wrinkle", "firming_lifting"],
    "collagen": ["firming_lifting"],
    "vitamin_c": ["brightening", "spot_fading", "anti_oxidant"],
    "niacinamide": ["brightening", "oil_control", "pore_refining"],
    "arbutin": ["brightening", "spot_fading"],
    "tranexamic_acid": ["brightening", "spot_fading"],
    "glabridin": ["brightening", "spot_fading"],
    "azelaic_acid": ["spot_fading", "anti_acne"],
    "kojic_acid": ["brightening", "spot_fading"],
    "pitera": ["brightening", "cell_renewal"],
    "salicylic_acid": ["oil_control", "pore_refining", "anti_acne", "exfoliating"],
    "aha": ["oil_control", "exfoliating"],
    "glycolic_acid": ["exfoliating"],
    "mandelic_acid": ["exfoliating"],
    "lha": ["oil_control", "exfoliating"],
    "pha": ["exfoliating", "hydrating"],
    "lactobionic_acid": ["exfoliating", "anti_oxidant"],
    "zinc_pca": ["oil_control"],
    "tea_tree": ["anti_acne"],
    "astaxanthin": ["anti_oxidant"],
    "ergothioneine": ["anti_oxidant"],
    "resveratrol": ["anti_oxidant", "anti_wrinkle"],
    "coq10": ["anti_oxidant", "anti_wrinkle"],
    "aloe": ["soothing", "hydrating"],
    "licorice_root": ["soothing", "anti_inflammatory"],
    "chamomile": ["soothing"],
    "calendula": ["soothing"],
    "mugwort": ["soothing", "anti_inflammatory"],
    "zinc_oxide": ["sun_protection"],
    "titanium_dioxide": ["sun_protection"],
    "chemical_uv_filters": ["sun_protection"],
}
for ing_code, eff_codes in efficacy_map.items():
    for eff_code in eff_codes:
        src = make_id("L2", "Ingredient", ing_code)
        tgt = make_id("L2", "Efficacy", eff_code)
        add_edge(src, tgt, "has_efficacy", "因果归因", "功效")

# --- Conflicts (7 from L2 4.1) ---
conflicts = [
    ("retinol", "aha", "需间隔使用", "12h+", "同时用刺激过大，可能损伤屏障"),
    ("retinol", "salicylic_acid", "需间隔使用", "12h+", "叠加去角质过度"),
    ("retinol", "vitamin_c", "需间隔使用", "12h+", "pH冲突，降低稳定性"),
    ("vitamin_c", "niacinamide", "降低效果", "10min+", "pH差异可能影响效果"),
    ("aha", "salicylic_acid", "不可同时使用", "", "叠加去角质过度"),
    ("retinol", "glycolic_acid", "不可同用", "", "三酸叠加屏障必崩"),
    ("vitamin_c", "aha", "需间隔使用", "12h+", "酸性叠加刺激"),
]
for a, b, ctype, interval, note in conflicts:
    src = make_id("L2", "Ingredient", a)
    tgt = make_id("L2", "Ingredient", b)
    add_edge(src, tgt, "conflicts_with", "互斥约束", "冲突", constraint_type=ctype, interval=interval, note=note)

# --- Synergies (12 from L2 4.2) ---
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
    ("vitamin_c", "panthenol", "VC + VE + 阿魏酸经典配方"),
]
for a, b, note in synergies:
    src = make_id("L2", "Ingredient", a)
    tgt = make_id("L2", "Ingredient", b)
    add_edge(src, tgt, "synergizes_with", "协同增强", "协同", note=note)

# --- Risk relationships (14 from L2 4.3) ---
risks = [
    ("retinol", "sensitive", "刺激、泛红、脱皮", "初次使用/高浓度"),
    ("retinol", "pregnant", "致畸风险", "孕期/备孕期禁用"),
    ("retinol", "acne_prone", "初期可能爆痘", "清洁反应2-4周消退"),
    ("aha", "sensitive", "刺激", "高浓度/角质薄"),
    ("salicylic_acid", "sensitive", "刺激", "敏感期不宜"),
    ("salicylic_acid", "pregnant", "孕妇慎用", "大面积使用需注意"),
    ("vitamin_c", "sensitive", "刺激、泛红", "高浓度/pH低"),
    ("niacinamide", "sensitive", "泛红", "浓度>5%"),
    ("alcohol", "sensitive", "刺激", "高浓度"),
    ("essential_oil", "sensitive", "过敏、光敏", "柑橘类精油光敏性强"),
    ("fragrance", "sensitive", "过敏", "累积性致敏"),
    ("tea_tree", "sensitive", "刺激", "高浓度/未稀释"),
    ("mineral_oil", "acne_prone", "闷痘", "高封闭性"),
    ("shea_butter", "acne_prone", "闷痘", "质地厚重"),
]
for ing, skin, risktype, condition in risks:
    src = make_id("L2", "Ingredient", ing)
    tgt = make_id("L0", "SkinType", skin)
    add_edge(src, tgt, "risk_for", "互斥约束", "风险", constraint_type=risktype, condition=condition)

# --- Tolerance relationships (6 from L2 4.4) ---
tolerances = [
    ("retinol", "4-8周", "从0.1%起步，三明治法"),
    ("retinal", "2-4周", "从低浓度起步→隔日→每日"),
    ("aha", "2-4周", "从5%起步→8%→10%→15%"),
    ("salicylic_acid", "1-2周", "从0.5%→1%→2%"),
    ("vitamin_c", "2-4周", "从5%→10%→15%→20%"),
    ("niacinamide", "1-2周", "从2%→5%→10%"),
]
for code, interval, note in tolerances:
    src = make_id("L2", "Ingredient", code)
    add_edge(src, src, "requires_tolerance", "互斥约束", "耐受", interval=interval, note=note, constraint_type="需耐受")

# --- Symptoms (24 from L2 section 5) ---
symptoms = [
    ("redness", "泛红", "repair.sensitive_soothe"),
    ("flaking", "脱皮", "hydration.basic_hydration"),
    ("tightness", "紧绷", "hydration.basic_hydration"),
    ("oiliness", "出油", "oil_control.sebum_control"),
    ("enlarged_pores", "毛孔粗大", "oil_control.pore_minimize"),
    ("fine_lines", "细纹", "anti_aging.fine_lines"),
    ("sagging", "松弛", "anti_aging.firming"),
    ("dullness", "暗沉", "brightening.dullness"),
    ("acne_active", "活痘", "acne.active_acne"),
    ("comedone", "闭口/粉刺", "acne.blackhead_comedone"),
    ("blackhead", "黑头", "acne.blackhead_comedone"),
    ("acne_mark_red", "红痘印", "acne.acne_scar"),
    ("acne_mark_dark", "黑痘印", "acne.acne_scar"),
    ("acne_pit", "痘坑", "acne.acne_scar"),
    ("stinging", "刺痛", "repair.sensitive_soothe"),
    ("itching", "瘙痒", "repair.sensitive_soothe"),
    ("roughness", "粗糙", "hydration"),
    ("dark_circles", "黑眼圈", "anti_aging.eye_aging"),
    ("eye_bags", "眼袋", "anti_aging.eye_aging"),
    ("neck_lines", "颈纹", "anti_aging.neck_care"),
    ("sunburn", "晒伤", "repair.sun_damage_repair"),
    ("uneven_tone", "肤色不均", "brightening.even_tone"),
    ("cakey_makeup", "卡粉", "makeup_fit.anti_cakey"),
    ("makeup_melt", "脱妆", "makeup_fit.long_lasting"),
]
for code, label, concern in symptoms:
    add_node("L2", "Symptom", code, label, concern=concern)

# --- Adverse Reactions (10 from L2 section 6) ---
reactions = [
    ("allergy", "过敏反应", "moderate-severe"),
    ("contact_dermatitis", "接触性皮炎", "severe"),
    ("breakout", "闷痘/爆痘", "mild-moderate"),
    ("purging", "清洁反应", "mild"),
    ("stinging_burning", "刺痛灼热", "mild-moderate"),
    ("pilling", "搓泥", "mild"),
    ("over_exfoliation", "过度去角质", "moderate-severe"),
    ("dryness_reaction", "异常干燥", "mild"),
    ("pigmentation", "色沉加重", "mild-moderate"),
    ("sensitivity_increase", "敏感度增加", "moderate"),
]
for code, label, severity in reactions:
    add_node("L2", "AdverseReaction", code, label, severity=severity)

# --- Makeup Techniques (10 from L2 section 7) ---
techniques = [
    ("base_prep", "底妆前护肤"),
    ("color_correct", "色彩校正"),
    ("spot_conceal", "点状遮瑕"),
    ("foundation_apply", "粉底上妆"),
    ("set_makeup", "定妆手法"),
    ("bake_technique", "烘焙定妆"),
    ("fix_cakey", "修复卡粉"),
    ("touch_up", "补妆技巧"),
    ("natural_glow", "自然光泽妆"),
    ("matte_finish", "雾面哑光妆"),
]
for code, label in techniques:
    add_node("L2", "Symptom", "tech_" + code, label)


# ================================================================
# L3: 方案层
# ================================================================

# --- Skincare Routines (7) ---
skincare_plans = [
    ("rt_001", "干皮基础保湿方案",
     ["温和清洁", "补水打底", "核心保湿精华", "封层锁水面霜", "日间防晒"],
     "dry,combination_dry", "hydration"),
    ("rt_002", "干敏肌换季修护方案",
     ["极简温和清洁", "核心修护精华", "屏障修护面霜", "温和防晒"],
     "dry+sensitive", "repair"),
    ("rt_003", "油痘肌控油祛痘方案",
     ["控油清洁", "水杨酸疏通(周期)", "控油修护精华", "轻薄保湿", "清爽防晒"],
     "oily+acne_prone", "acne,oil_control"),
    ("rt_004", "痘印淡化方案",
     ["淡印精华(烟酰胺/传明酸)", "温和酸促代谢(隔日)", "严格防晒"],
     "all", "acne.acne_scar,brightening"),
    ("rt_005", "初老抗老入门方案(25-30岁)",
     ["日间抗氧化精华(VC)", "夜间修护精华(A醇/多肽)", "眼周护理", "保湿面霜", "防晒抗光老化"],
     "all", "anti_aging"),
    ("rt_006", "美白提亮方案",
     ["日间美白精华(VC/烟酰胺)", "夜间促代谢(A醇/果酸)", "严格防晒SPF50+"],
     "all(非敏感期)", "brightening"),
    ("rt_007", "孕期安全护肤方案",
     ["温和清洁", "基础保湿面霜", "纯物理防晒"],
     "all", "hydration,repair"),
]
for code, label, steps, skin, concern in skincare_plans:
    add_node("L3", "SkincarePlan", code, label, steps=steps, suitableSkin=skin, targetConcern=concern)

# --- Aftersales Playbooks (4) ---
aftersales = [
    ("ap_001", "过敏刺痛应对方案",
     ["停用可疑产品", "简化护肤清水+保湿", "严重就医"],
     "allergy,stinging_burning"),
    ("ap_002", "闷痘爆痘应对方案",
     ["判断purging vs过敏", "停用可疑产品或降频", "简化护肤"],
     "breakout,purging"),
    ("ap_003", "搓泥解决方案",
     ["等吸收再涂下层", "减少用量薄涂", "减少护肤步骤"],
     "pilling"),
    ("ap_004", "过度去角质修护方案",
     ["停用所有活性成分", "极简修护(积雪草/泛醇/神经酰胺)", "物理防晒", "4-8周修复期"],
     "over_exfoliation"),
]
for code, label, steps, trigger in aftersales:
    add_node("L3", "SkincarePlan", code, label, steps=steps, targetConcern=trigger)

# --- Makeup Looks (3) ---
makeup_plans = [
    ("ml_001", "油皮通勤持妆妆",
     ["控油妆前乳", "哑光粉底按压上妆", "遮瑕点涂", "散粉T区烘焙定妆", "午间补妆"],
     "oily,combination_oily"),
    ("ml_002", "干皮伪素颜妆",
     ["保湿打底", "水润粉底美妆蛋弹涂", "保湿遮瑕", "定妆喷雾"],
     "dry,combination_dry"),
    ("ml_003", "急救遮瑕方案",
     ["色彩校正(绿遮红/橘遮紫)", "肤色遮瑕点涂", "散粉定妆"],
     "all"),
]
for code, label, steps, skin in makeup_plans:
    add_node("L3", "SkincarePlan", code, label, steps=steps, suitableSkin=skin, targetConcern="makeup")

# --- Promo Strategies (2) ---
promo_plans = [
    ("ps_001", "大促省钱通用策略",
     ["预热领券", "付定金锁预售价", "尾款叠加满减+店铺券", "关注价保"],
     "all"),
    ("ps_002", "按预算分配囤货策略",
     ["极低预算买急需1-2件", "平价选套组凑满减", "中等预算完整方案", "高端趁大促囤半年"],
     "all"),
]
for code, label, steps, skin in promo_plans:
    add_node("L3", "SkincarePlan", code, label, steps=steps, suitableSkin=skin, targetConcern="promotion")


# ================================================================
# L4: 对话引擎层
# ================================================================

# --- Channel routing (5 channels) ---
channels = [
    ("ch_aftersales", "售后Channel", "aftersales", 1),
    ("ch_promotion", "大促Channel", "promotion", 2),
    ("ch_makeup", "妆教Channel", "makeup", 3),
    ("ch_skincare", "护肤Channel", "skincare", 4),
    ("ch_chat", "闲聊Channel", "chat", 5),
]
for code, label, channel, priority in channels:
    add_node("L4", "Intent", code, label, channel=channel, priority=priority)

# --- Primary intents (7 types) ---
intents_primary = [
    ("emotional_entry", "情绪入口", "all", 1),
    ("seek_solution", "求解决方案", "skincare", 2),
    ("seek_knowledge", "求知识/答疑", "skincare", 3),
    ("seek_recommendation", "求推荐", "skincare", 4),
    ("seek_procedure", "求操作指导", "all", 5),
    ("seek_comparison", "求比较", "skincare", 6),
    ("casual_chat", "闲聊", "chat", 99),
]
for code, label, channel, priority in intents_primary:
    add_node("L4", "Intent", code, label, channel=channel, priority=priority)

# --- Secondary intents (skincare) ---
intents_skincare = [
    ("confirm_combo", "确认搭配", "skincare", 10),
    ("usage_detail", "使用方法", "skincare", 11),
    ("risk_check", "风险检查", "skincare", 12),
    ("budget_adjust", "预算调整", "skincare", 13),
    ("add_concern", "追加诉求", "skincare", 14),
    ("confirm_purchase", "确认购买", "skincare", 15),
]
for code, label, channel, priority in intents_skincare:
    add_node("L4", "Intent", code, label, channel=channel, priority=priority)

# --- Secondary intents (promotion) ---
intents_promo = [
    ("coupon_stack", "券叠加咨询", "promotion", 10),
    ("timing_inquiry", "时间咨询", "promotion", 11),
    ("refund_inquiry", "退款咨询", "promotion", 12),
    ("channel_switch", "渠道咨询", "promotion", 13),
    ("promo_compare", "活动比较", "promotion", 14),
]
for code, label, channel, priority in intents_promo:
    add_node("L4", "Intent", code, label, channel=channel, priority=priority)

# --- Secondary intents (aftersales) ---
intents_after = [
    ("report_reaction", "报告反应", "aftersales", 10),
    ("identify_cause", "排查原因", "aftersales", 11),
    ("seek_remedy", "求补救", "aftersales", 12),
    ("return_request", "退货请求", "aftersales", 13),
]
for code, label, channel, priority in intents_after:
    add_node("L4", "Intent", code, label, channel=channel, priority=priority)

# --- Secondary intents (makeup) ---
intents_makeup = [
    ("technique_inquiry", "技巧咨询", "makeup", 10),
    ("product_for_look", "妆容选品", "makeup", 11),
    ("adapt_for_skin", "肤质适配", "makeup", 12),
    ("fix_problem", "妆容修复", "makeup", 13),
]
for code, label, channel, priority in intents_makeup:
    add_node("L4", "Intent", code, label, channel=channel, priority=priority)

# --- Dialogue states ---
dialogue_states = [
    ("state_exploring", "探索状态"),
    ("state_narrowing", "收窄状态"),
    ("state_comparing", "比较状态"),
    ("state_decided", "已决定状态"),
]
for code, label in dialogue_states:
    add_node("L4", "Intent", code, label, channel="all", priority=0)


# ================================================================
# L5: 词汇归一化层
# ================================================================

def add_synonym(code, canonical, variants, target_layer, target_type, target_code):
    """Add a synonym mapping node and maps_to edge."""
    nid = add_node("L5", "SynonymMapping", code, canonical, canonical=canonical, variants=variants, target=target_code)
    tid = make_id(target_layer, target_type, target_code)
    if tid in node_ids:
        add_edge(nid, tid, "maps_to", "等价映射", "映射")
    return nid


# --- 1. Skin type synonyms ---
skin_synonyms = [
    ("syn_dry", "干皮", ["干皮", "干性皮肤", "干性肌肤", "皮肤干", "脸干"], "L0", "SkinType", "dry"),
    ("syn_oily", "油皮", ["油皮", "油性皮肤", "大油皮", "大油田", "油光满面"], "L0", "SkinType", "oily"),
    ("syn_combination", "混合肌", ["混合肌", "混合皮", "混合型", "混合性"], "L0", "SkinType", "combination"),
    ("syn_combo_oily", "混油皮", ["混油皮", "混合偏油", "混合偏油肌"], "L0", "SkinType", "combination_oily"),
    ("syn_combo_dry", "混干皮", ["混干皮", "混合偏干", "混合偏干肌"], "L0", "SkinType", "combination_dry"),
    ("syn_sensitive", "敏感肌", ["敏感肌", "敏皮", "敏感皮肤", "敏感性皮肤"], "L0", "SkinType", "sensitive"),
    ("syn_neutral", "中性皮", ["中性皮肤", "中性肌", "不油不干"], "L0", "SkinType", "neutral"),
]
for code, canonical, variants, tl, tt, tc in skin_synonyms:
    add_synonym(code, canonical, variants, tl, tt, tc)

# Composite skin type synonyms
composite_skin = [
    ("syn_dry_sensitive", "干敏肌", ["干敏肌", "敏感干皮", "又干又敏感"], "L0", "SkinType", "dry"),
    ("syn_oily_sensitive", "油敏肌", ["油敏肌", "油皮但敏感"], "L0", "SkinType", "oily"),
    ("syn_oily_acne", "油痘肌", ["油痘肌", "油皮爱长痘"], "L0", "SkinType", "oily"),
    ("syn_dehydrated", "外油内干", ["外油内干", "出油但紧绷", "缺水性油皮"], "L0", "SkinType", "oily"),
    ("syn_tolerant", "城墙皮", ["城墙皮", "啥都能用"], "L0", "SkinType", "mod_tolerant"),
]
for code, canonical, variants, tl, tt, tc in composite_skin:
    add_synonym(code, canonical, variants, tl, tt, tc)

# --- 2. Symptom synonyms ---
symptom_synonyms = [
    ("syn_dryness", "干燥", ["干、干燥、起皮、紧绷、拔干、脱皮、缺水"], "L2", "Symptom", "flaking"),
    ("syn_oiliness", "出油", ["出油、油光、冒油、油光满面、能炒菜"], "L2", "Symptom", "oiliness"),
    ("syn_pores", "毛孔粗大", ["毛孔粗大、毛孔大、鼻翼毛孔、橘皮"], "L2", "Symptom", "enlarged_pores"),
    ("syn_blackhead", "黑头", ["黑头、草莓鼻、鼻子上黑点"], "L2", "Symptom", "blackhead"),
    ("syn_redness", "泛红", ["泛红、脸红、红血丝、两颊红、苹果脸"], "L2", "Symptom", "redness"),
    ("syn_stinging", "刺痛", ["刺痛、火辣辣、蜇、有刺感"], "L2", "Symptom", "stinging"),
    ("syn_acne", "痘痘", ["痘痘、长痘、反复长痘、爆痘、冒痘、脓包"], "L2", "Symptom", "acne_active"),
    ("syn_comedone", "闭口", ["闭口、闭口粉刺、小闭口、小疙瘩"], "L2", "Symptom", "comedone"),
    ("syn_acne_mark_r", "红痘印", ["红痘印、痘印发红、红色印子"], "L2", "Symptom", "acne_mark_red"),
    ("syn_acne_mark_d", "黑痘印", ["黑痘印、痘印发黑、褐色印子"], "L2", "Symptom", "acne_mark_dark"),
    ("syn_acne_pit", "痘坑", ["痘坑、凹坑、凹痘疤"], "L2", "Symptom", "acne_pit"),
    ("syn_dullness", "暗沉", ["暗沉、黄气、发黄、蜡黄、没光泽、气色差"], "L2", "Symptom", "dullness"),
    ("syn_fine_lines", "细纹", ["细纹、干纹、鱼尾纹、额头纹、小纹路"], "L2", "Symptom", "fine_lines"),
    ("syn_sagging", "松弛", ["松弛、下垂、不紧致、轮廓模糊、垮了"], "L2", "Symptom", "sagging"),
    ("syn_dark_circles", "黑眼圈", ["黑眼圈、熊猫眼、眼下发黑"], "L2", "Symptom", "dark_circles"),
    ("syn_cakey", "卡粉", ["卡粉、起皮卡粉、浮粉、斑驳"], "L2", "Symptom", "cakey_makeup"),
    ("syn_melt", "脱妆", ["脱妆、花妆、妆花了"], "L2", "Symptom", "makeup_melt"),
]
for code, canonical, variants, tl, tt, tc in symptom_synonyms:
    add_synonym(code, canonical, variants, tl, tt, tc)

# --- 3. Ingredient synonyms (35 from L5 section 3) ---
ingredient_synonyms = [
    ("syn_retinol", "A醇", ["A醇", "视黄醇", "早C晚A的A", "va"], "retinol"),
    ("syn_retinal", "A醛", ["A醛", "视黄醛"], "retinal"),
    ("syn_vc", "维C", ["VC", "维C", "抗坏血酸", "早C晚A的C", "左旋C", "原型C"], "vitamin_c"),
    ("syn_nia", "烟酰胺", ["烟酰胺", "VB3", "B3"], "niacinamide"),
    ("syn_ha", "玻尿酸", ["玻尿酸", "透明质酸", "HA", "水光成分"], "hyaluronic_acid"),
    ("syn_cer", "神经酰胺", ["神经酰胺", "Ceramide", "神酰"], "ceramide"),
    ("syn_bha", "水杨酸", ["水杨酸", "BHA", "超分子水杨酸"], "salicylic_acid"),
    ("syn_aha", "果酸", ["果酸", "AHA", "刷酸"], "aha"),
    ("syn_glycolic", "甘醇酸", ["甘醇酸"], "glycolic_acid"),
    ("syn_mandelic", "杏仁酸", ["杏仁酸"], "mandelic_acid"),
    ("syn_centella", "积雪草", ["积雪草", "老虎草", "CICA", "马齿苋"], "centella"),
    ("syn_squalane", "角鲨烷", ["角鲨烷"], "squalane"),
    ("syn_peptide", "多肽", ["多肽", "胜肽"], "peptide"),
    ("syn_hexapeptide", "六胜肽", ["六胜肽", "类肉毒素"], "hexapeptide"),
    ("syn_bosein", "玻色因", ["玻色因", "波色因", "Pro-Xylane"], "bosein"),
    ("syn_panthenol", "泛醇", ["泛醇", "VB5", "B5", "维B5"], "panthenol"),
    ("syn_bifida", "二裂酵母", ["二裂酵母", "酵母精粹", "Bifida"], "bifida_ferment"),
    ("syn_tranexamic", "传明酸", ["传明酸", "氨甲环酸", "凝血酸"], "tranexamic_acid"),
    ("syn_azelaic", "壬二酸", ["壬二酸", "杜鹃花酸"], "azelaic_acid"),
    ("syn_arbutin", "熊果苷", ["熊果苷", "α-熊果苷"], "arbutin"),
    ("syn_glabridin", "光甘草定", ["光甘草定", "甘草提取物"], "glabridin"),
    ("syn_astaxanthin", "虾青素", ["虾青素"], "astaxanthin"),
    ("syn_ergothioneine", "麦角硫因", ["麦角硫因"], "ergothioneine"),
    ("syn_ectoin", "依克多因", ["依克多因"], "ectoin"),
    ("syn_resveratrol", "白藜芦醇", ["白藜芦醇"], "resveratrol"),
    ("syn_coq10", "辅酶Q10", ["辅酶Q10", "CoQ10", "Q10"], "coq10"),
    ("syn_allantoin", "尿囊素", ["尿囊素"], "allantoin"),
    ("syn_collagen", "胶原蛋白", ["胶原蛋白", "胶原"], "collagen"),
    ("syn_pitera", "PITERA", ["PITERA", "半乳糖酵母样菌发酵液", "P家精华"], "pitera"),
    ("syn_alcohol", "酒精", ["酒精", "乙醇", "含酒精"], "alcohol"),
    ("syn_fragrance", "香精", ["香精", "有香味", "人工香料"], "fragrance"),
    ("syn_silicone", "硅油", ["硅油", "聚二甲基硅氧烷", "假滑成分"], "silicone"),
    ("syn_mineral_oil", "矿物油", ["矿物油"], "mineral_oil"),
]
for code, canonical, variants, target in ingredient_synonyms:
    nid = add_node("L5", "SynonymMapping", code, canonical, canonical=canonical, variants=variants, target=target)
    tid = make_id("L2", "Ingredient", target)
    if tid in node_ids:
        add_edge(nid, tid, "maps_to", "等价映射", "映射")

# --- 4. Brand synonyms (36 from L5 section 4) ---
brand_synonyms = [
    ("syn_estee", "雅诗兰黛", ["雅诗兰黛", "雅诗", "EL", "雅家"], "estee_lauder"),
    ("syn_lancome", "兰蔻", ["兰蔻", "兰家", "Lancôme"], "lancome"),
    ("syn_kiehls", "科颜氏", ["科颜氏", "科家", "契尔氏", "Kiehl's"], "kiehls"),
    ("syn_lamer", "海蓝之谜", ["海蓝之谜", "lamer", "LM", "海洋之谜"], "la_mer"),
    ("syn_helena", "赫莲娜", ["赫莲娜", "HR"], "helena"),
    ("syn_sk2", "SK-II", ["SK-II", "SK2", "SKII", "SK二"], "sk_ii"),
    ("syn_shiseido", "资生堂", ["资生堂", "资家"], "shiseido"),
    ("syn_decorte", "黛珂", ["黛珂", "DQ"], "decorte"),
    ("syn_clinique", "倩碧", ["倩碧"], "clinique"),
    ("syn_clarins", "娇韵诗", ["娇韵诗"], "clarins"),
    ("syn_origins", "悦木之源", ["悦木之源", "品木宣言"], "origins"),
    ("syn_curel", "珂润", ["珂润", "Curél"], "curel"),
    ("syn_ipsa", "茵芙莎", ["IPSA", "茵芙莎"], "ipsa"),
    ("syn_loreal", "欧莱雅", ["欧莱雅", "欧家", "L'Oréal"], "loreal"),
    ("syn_cerave", "CeraVe", ["CeraVe", "适乐肤"], "cerave"),
    ("syn_to", "The Ordinary", ["TO", "The Ordinary", "ordinary"], "the_ordinary"),
    ("syn_proya", "珀莱雅", ["珀莱雅", "PROYA"], "proya"),
    ("syn_winona", "薇诺娜", ["薇诺娜"], "winona"),
    ("syn_uniskin", "优时颜", ["优时颜"], "uniskin"),
    ("syn_marubi", "丸美", ["丸美"], "marubi"),
    ("syn_guyu", "谷雨", ["谷雨"], "guyu"),
    ("syn_skinceuticals", "修丽可", ["修丽可", "杜克", "SC"], "skinceuticals"),
    ("syn_lrp", "理肤泉", ["理肤泉", "LRP"], "lrp"),
    ("syn_avene", "雅漾", ["雅漾"], "avene"),
    ("syn_freeplus", "芙丽芳丝", ["芙丽芳丝", "freeplus", "FP"], "freeplus"),
    ("syn_comfy", "可复美", ["可复美"], "comfy"),
    ("syn_dryu", "玉泽", ["玉泽", "Dr.Yu"], "dryu"),
    ("syn_betterderm", "博乐达", ["博乐达"], "betterderm"),
    ("syn_timage", "彩棠", ["彩棠"], "timage"),
    ("syn_maogeping", "毛戈平", ["毛戈平", "MGP"], "maogeping"),
    ("syn_florasis", "花西子", ["花西子"], "florasis"),
    ("syn_zhuben", "逐本", ["逐本"], "zhuben"),
    ("syn_zhiben", "至本", ["至本"], "zhiben"),
    ("syn_quadha", "夸迪", ["夸迪"], "quadha"),
    ("syn_anessa", "安热沙", ["安热沙", "安耐晒"], "anessa"),
    ("syn_fuyijia", "敷尔佳", ["敷尔佳"], "fuyijia"),
]
for code, canonical, variants, target in brand_synonyms:
    nid = add_node("L5", "SynonymMapping", code, canonical, canonical=canonical, variants=variants, target=target)
    tid = make_id("L1", "Brand", target)
    if tid in node_ids:
        add_edge(nid, tid, "maps_to", "等价映射", "映射")

# --- 5. Product nickname synonyms ---
product_synonyms = [
    ("syn_little_black", "小黑瓶", ["小黑瓶", "兰蔻精华", "黑瓶"], "little_black"),
    ("syn_little_brown", "小棕瓶", ["小棕瓶", "雅诗兰黛精华", "棕瓶"], "little_brown"),
    ("syn_fairy_water", "神仙水", ["神仙水", "SKII精华", "护肤精华露"], "fairy_water"),
    ("syn_double_anti", "双抗", ["双抗", "珀莱雅双抗", "双抗精华"], "double_anti"),
    ("syn_ruby", "红宝石", ["红宝石", "珀莱雅红宝石"], "ruby"),
    ("syn_black_bind", "黑绷带", ["黑绷带", "赫莲娜黑绷带"], "black_bindage"),
    ("syn_ce", "CE精华", ["CE精华", "修丽可CE"], "ce_serum"),
    ("syn_purple_iron", "紫铁", ["紫铁", "科颜氏紫铁"], "purple_iron"),
    ("syn_gold_bottle", "金瓶防晒", ["金瓶防晒", "安热沙金瓶", "小金瓶"], "gold_bottle"),
    ("syn_blue_fat", "蓝胖子", ["蓝胖子", "资生堂防晒"], "blue_fat"),
    ("syn_white_tube", "小白管", ["小白管", "兰蔻防晒"], "white_tube"),
    ("syn_exbf_mask", "前男友面膜", ["前男友面膜", "SKII面膜"], "ex_bf_mask"),
]
for code, canonical, variants, target in product_synonyms:
    nid = add_node("L5", "SynonymMapping", code, canonical, canonical=canonical, variants=variants, target=target)
    tid = make_id("L1", "SPU", target)
    if tid in node_ids:
        add_edge(nid, tid, "maps_to", "等价映射", "映射")

# --- 6. Promo term synonyms (13 from L5 section 5) ---
promo_synonyms = [
    ("syn_deposit", "定金", ["定金", "预付款", "订金"]),
    ("syn_final_pay", "尾款", ["尾款", "余款", "补差价", "补尾款"]),
    ("syn_full_reduce", "满减", ["满减", "跨店满减", "满XX减XX", "凑满减"]),
    ("syn_coupon", "优惠券", ["优惠券", "券", "红包", "优惠码", "领券"]),
    ("syn_brand_coupon", "店铺券", ["店铺券", "品牌券", "回购券", "会员券"]),
    ("syn_gift", "赠品", ["赠品", "买赠", "送的", "附赠", "小样"]),
    ("syn_bundle", "凑单", ["凑单", "凑满减", "拼单", "凑够"]),
    ("syn_presale", "预售", ["预售", "预定", "提前购", "预售价"]),
    ("syn_price_guarantee", "价保", ["价保", "保价", "退差价", "降价退差"]),
    ("syn_loyalty", "亲密度", ["亲密度", "粉丝值", "粉丝等级", "粉丝价"]),
    ("syn_refund", "退货", ["退货", "退款", "退了", "不想要了", "7天无理由"]),
    ("syn_shipping", "发货", ["发货", "什么时候发", "物流", "快递"]),
    ("syn_free_ship", "包邮", ["包邮", "免运费"]),
]
for code, canonical, variants in promo_synonyms:
    add_node("L5", "SynonymMapping", code, canonical, canonical=canonical, variants=variants, target="promo_term")

# --- 7. Concern/risk synonyms (8 from L5 section 6) ---
concern_synonyms = [
    ("syn_fear_breakout", "怕闷痘", ["闷痘", "会不会长痘", "闷不闷", "堵毛孔"]),
    ("syn_fear_irritation", "怕刺激", ["刺激", "太猛", "容易过敏", "不耐受", "烂脸"]),
    ("syn_fear_greasy", "怕油腻", ["太油", "黏糊糊", "厚重", "沾枕头", "不清爽"]),
    ("syn_fear_pilling", "怕搓泥", ["搓泥", "起泥", "搓出东西"]),
    ("syn_fear_photosensitive", "怕光敏", ["光敏", "用了能晒太阳吗", "白天能用吗"]),
    ("syn_fear_dependency", "怕依赖", ["依赖", "停了反弹", "越用越离不开"]),
    ("syn_fear_purging", "怕爆痘", ["爆痘", "排毒反应", "用了会爆吗"]),
    ("syn_fear_interaction", "怕冲突", ["冲突", "打架", "一起用会不会有问题"]),
]
for code, canonical, variants in concern_synonyms:
    add_node("L5", "SynonymMapping", code, canonical, canonical=canonical, variants=variants, target="concern")

# --- 8. Social media hot words (20 from L5 section 9) ---
hot_words = [
    ("syn_early_c_late_a", "早C晚A", ["早C晚A"], "combination_method"),
    ("syn_acid_freedom", "刷酸自由", ["刷酸自由"], "acid_usage"),
    ("syn_ingredient_fan", "成分党", ["成分党"], "user_tag"),
    ("syn_oil_nourish", "以油养肤", ["以油养肤"], "oil_method"),
    ("syn_sandwich", "三明治法", ["三明治法"], "tolerance_method"),
    ("syn_skincare_foundation", "养肤粉底", ["养肤粉底"], "hybrid_product"),
    ("syn_makeup_skincare", "妆养合一", ["妆养合一"], "hybrid_product"),
    ("syn_overnight_rescue", "熬夜急救", ["熬夜急救"], "scenario"),
    ("syn_season_stable", "换季维稳", ["换季维稳"], "scenario"),
    ("syn_lazy_skincare", "懒人护肤", ["懒人护肤"], "minimal_routine"),
    ("syn_dupe", "平替", ["平替", "贵替"], "product_relation"),
    ("syn_empty_bottle", "空瓶记", ["空瓶记"], "review_type"),
    ("syn_avoid", "拔草", ["拔草"], "negative_review"),
    ("syn_recommend", "种草", ["种草"], "positive_review"),
    ("syn_repurchase", "回购", ["回购"], "positive_signal"),
    ("syn_bad_exp", "踩雷", ["踩雷"], "negative_review"),
    ("syn_ruined_face", "烂脸", ["烂脸"], "severe_damage"),
    ("syn_fortress_skin", "城墙皮", ["城墙皮"], "tolerant_skin"),
    ("syn_moon_surface", "月球表面", ["月球表面"], "severe_acne_pit"),
    ("syn_desert_face", "沙漠脸", ["沙漠脸"], "extreme_dryness"),
]
for code, canonical, variants, target in hot_words:
    add_node("L5", "SynonymMapping", code, canonical, canonical=canonical, variants=variants, target=target)

# --- 9. Ambiguous word mappings (11 from L5 section 8) ---
ambiguous = [
    ("syn_amb_deposit", "定金vs订金", ["定金", "订金"], "disambiguation"),
    ("syn_amb_isolation", "隔离", ["隔离"], "disambiguation"),
    ("syn_amb_essence", "精华", ["精华"], "disambiguation"),
    ("syn_amb_water", "水", ["水"], "disambiguation"),
    ("syn_amb_milk", "乳", ["乳"], "disambiguation"),
    ("syn_amb_acid", "刷酸", ["刷酸"], "disambiguation"),
    ("syn_amb_dupe", "平替", ["平替"], "disambiguation"),
    ("syn_amb_set", "套组", ["套组"], "disambiguation"),
    ("syn_amb_acne_mark", "痘印", ["痘印"], "disambiguation"),
    ("syn_amb_sensitive", "敏感", ["敏感"], "disambiguation"),
    ("syn_amb_photosensitive", "光敏", ["光敏"], "disambiguation"),
]
for code, canonical, variants, target in ambiguous:
    add_node("L5", "SynonymMapping", code, canonical, canonical=canonical, variants=variants, target=target)


# ================================================================
# Post-processing: SPU → Ingredient edges (now that L2 nodes exist)
# ================================================================
for spu_data in spus:
    code, label, brand, category, aliases, key_ing = spu_data
    if not key_ing:
        continue
    src = make_id("L1", "SPU", code)
    for ing in key_ing.split(","):
        ing = ing.strip()
        if ing:
            tgt = make_id("L2", "Ingredient", ing)
            add_edge(src, tgt, "contains", "组成归属", "含有")


# ================================================================
# Write output
# ================================================================
os.makedirs(OUT, exist_ok=True)
with open(os.path.join(OUT, "nodes.json"), "w", encoding="utf-8") as f:
    json.dump(nodes, f, ensure_ascii=False, indent=2)
with open(os.path.join(OUT, "edges.json"), "w", encoding="utf-8") as f:
    json.dump(edges, f, ensure_ascii=False, indent=2)

# Print stats by layer
from collections import Counter
layer_counts = Counter(n["data"]["layer"] for n in nodes)
type_counts = Counter(n["data"]["entityType"] for n in nodes)
print(f"\nGenerated {len(nodes)} nodes and {len(edges)} edges")
print(f"\nBy layer:")
for layer in sorted(layer_counts.keys()):
    print(f"  {layer}: {layer_counts[layer]} nodes")
print(f"\nBy entity type:")
for etype in sorted(type_counts.keys()):
    print(f"  {etype}: {type_counts[etype]} nodes")
print(f"\nOutput: {OUT}/nodes.json, {OUT}/edges.json")

# demonslayer-site — Demon Slayer Wiki (鬼灭之刃)

---
MANDATORY_RULES_REF: specs/MANDATORY_RULES.md
STATUS: 本spec受MANDATORY_RULES.md约束，冲突时以总法为准。
---

## 基本信息

| 属性 | 值 |
|------|-----|
| 目录 | `demonslayer-site/` |
| 域名 | demonslayer.jycsd.com |
| 站点名称 | Demon Slayer Corps |
| 品牌色 | `#0F766E` (翠绿) + `#0C0A09` (近黑底) |
| 类型 | 暗色底 anime 模板 |
| 受众 | 全球动漫迷 |
| 月搜索量 | 1500万+ |
| 模板类型 | anime 标准模板 (暗色) |
| 品牌 | Myers Media / Jordan Myers |

## 页面结构

```
demonslayer-site/
├── index.html / about.html / contact.html / privacy-policy.html
├── terms.html / cookie-policy.html / sitemap.xml
├── robots.txt / ads.txt / favicon.ico
├── images/
│   ├── default-og.jpg / logo.svg
│   ├── characters/         # 角色图 (15角色×3=45张)
│   ├── hashira/            # 柱 (9柱×3=27张)
│   ├── demons/             # 鬼 (12鬼×2=24张)
│   ├── weapons/            # 武器 (5张)
│   ├── locations/          # 地点 (5张)
│   └── banners/
├── characters/             # 15个主要角色页
├── characters/index.html   # 角色索引 (15个)
├── breathing-styles/       # 14种呼吸法
├── breathing-styles/index.html # 呼吸法索引 (14种)
├── arcs/                   # 12个篇章
├── arcs/index.html         # 篇章索引 (12个)
├── demons/                 # 12鬼
├── demons/index.html       # 鬼索引 (12个)
├── hashira/                # 9柱
├── hashira/index.html      # 柱索引 (9个)
├── weapons/                # 武器与日轮刀 (5页)
├── weapons/index.html      # 武器索引
├── training/               # 训练与技法 (5页)
├── training/index.html     # 训练索引
├── locations/              # 地点与世界 (5页)
├── locations/index.html    # 地点索引
├── corps/                  # 鬼杀队 (5页)
├── corps/index.html        # 鬼杀队索引
├── blood-arts/             # 血鬼术 (5页)
├── blood-arts/index.html   # 血鬼术索引
└── index.html
```

总计约 **100页**。

> 参照站: aot-site (动漫站模板)。每个分类子目录必须有 index.html 作为该分类的全部条目列表页。首页 'View All' 按钮链接到对应 guides/*/index.html。

## 分类设计

### 1. Characters (角色, 15个)
- Tanjiro / Nezuko / Zenitsu / Inosuke / Kanao / Genya / Aoi / Murata / Sabito / Makomo / Urokodaki / Rengoku Family / Ubuyashiki / Tamayo / Yushiro
- 每页: 角色大图+信息表+简介+战斗风格+相关角色

### 2. Hashira (柱, 9个)
- Giyu Tomioka (水) / Shinobu Kocho (虫) / Kyojuro Rengoku (炎) / Tengen Uzui (音) / Mitsuri Kanroji (恋) / Muichiro Tokito (霞) / Gyomei Himejima (岩) / Obanai Iguro (蛇) / Sanemi Shinazugawa (风)
- 每页: 柱大图+呼吸法+战绩+名场面

### 3. Breathing Styles (呼吸法, 14种)
- Water / Flame / Thunder / Wind / Stone / Insect / Sound / Love / Mist / Serpent / Sun (Hinokami Kagura) / Moon / Flower / Beast
- 每页: 呼吸法招式列表+使用者+战斗场景

### 4. Arcs (篇章, 12个)
- Final Selection / First Mission / Asakusa / Tsuzumi Mansion / Mount Natagumo / Rehabilitation Training / Mugen Train / Entertainment District / Swordsmith Village / Hashira Training / Infinity Castle / Sunrise Countdown
- 每页: 篇章概述+关键战斗+角色发展

### 5. Demons (鬼, 12个)
- Muzan Kibutsuji / Kokushibo / Doma / Akaza / Hantengu / Gyokko / Daki & Gyutaro / Enmu / Rui / Yahaba / Susamaru / Hand Demon
- 每页: 鬼图+能力+血鬼术+与主角冲突

### 6. Weapons & Swords (武器与日轮刀)
- Nichirin Swords Complete Guide: How Nichirin blades are forged, color meanings (Black/Red/Blue/Yellow/Green/Pink/White/Gray)
- Tanjiro's Black Sword: Significance, theories, Sun Breathing connection
- Nichirin Blade Creation Process: Scarlet Crimson Iron Sand, Scarlet Ore, swordsmithing traditions
- Specialized Demon Slayer Weapons: Shinobu's poison blade, Mitsuri's whip sword, Tengen's dual cleavers, Gyomei's flail and axe
- Weapon Modifications & Enhancements: Bright red blades, wisteria coating, sword grip variations

### 7. Training & Techniques (训练与技法)
- Demon Slayer Training Methods: Total Concentration Breathing, Waterfall and gourd training
- Hashira Training Arc Deep Dive: All 7 training stations and what each Hashira taught
- Breathing Technique Mastery: Progression from basic breathing to creating new forms
- Physical Conditioning: Nichirin sword weight training, stamina building, reflexes enhancement
- Demon Slayer Exam: Final Selection process, survival rate, wisteria, what recruits face

### 8. Locations & World (地点与世界)
- Demon Slayer World Map: Major locations, distances, travel methods (Taisho era Japan)
- Mount Fujikasane & Final Selection Site: Wisteria barrier, demon prison environment
- Swordsmith Village: Hidden village, hot springs, Yoriichi Type Zero doll, village culture
- Infinity Castle: Nakime's control, spatial manipulation, castle layout, teleportation mechanics
- Important Locations Guide: Asakusa, Mugen Train, Yoshiwara Entertainment District, Mount Natagumo

### 9. Demon Slayer Corps (鬼杀队)
- Demon Slayer Corps Organization: Ubuyashiki family, Hashira council, Kakushi, swordsmiths hierarchy
- Ranks & Rankings Guide: Kanoe → Hinoe → Hashira progression, salary system, Kasugai Crows
- The Ubuyashiki Family: Curse, leadership, Kagaya's role, legacy and sacrifice
- Kakushi & Support Roles: Cleanup brigade, medical support, logistics explained
- Demon Slayer Marks: Origin, awakening conditions, mark connection, Transparent World, Crimson Red Blade, Selfless State

### 10. Blood Demon Arts (血鬼术)
- Blood Demon Art System: How demons develop BDA, Muzan's blood, power scaling
- Upper Moon Blood Demon Arts: Complete catalog of all Upper Moon BDAs with combat analysis
- Lower Moon Blood Demon Arts: Enmu, Rui, and notable Lower Moon BDAs explained
- Blood Demon Art vs Breathing Techniques: Power comparison, strengths and weaknesses, key battles
- Unique & Special Blood Demon Arts: Nezuko's Exploding Blood, Tamayo's hallucinations, Yushiro's concealment

## 图片清单

| 类型 | 数量 | 来源 |
|------|------|------|
| 角色图 | 45 | pngwing.com + 官方素材 |
| 柱图 | 27 | pngwing.com |
| 鬼图 | 24 | pngwing.com |
| 武器图 | 5 | pngwing.com |
| 地点图 | 5 | 官方壁纸 |
| Banner | 8 | 官方壁纸 |

## 首页区块

1. **Hero Banner**: 轮播≥6张 (Tanjiro + Nezuko + 9柱中精选6)
2. **Featured Characters**: 角色轮播 (4-6/行)
3. **Hashira Showcase**: 9柱卡片网格
4. **Breathing Styles**: 呼吸法快速导航
5. **Story Arcs**: 篇章卡片
6. **Weapons & Swords**: 日轮刀与武器展示
7. **Training & Techniques**: 训练方法快速导航
8. **Locations & World**: 大正时代世界地图入口
9. **Demon Slayer Corps**: 鬼杀队组织架构展示
10. **Blood Demon Arts**: 血鬼术分类与对比
11. **AdSense**: 3个广告位

## CTR与流量增长策略

### 标题优化
- 角色页: "Tanjiro Kamado - Complete Guide: Breathing Styles, Abilities & Story Arc"
- 柱页: "Kyojuro Rengoku - The Flame Hashira: Powers, Battles & Legacy"
- 格式: `[Character Name] - [Title/Role]: [Key Abilities/Story]`

### Meta Description
- 角色核心信息+剧情诱饵
- 例: "Tanjiro Kamado is the main protagonist of Demon Slayer. Learn his Water Breathing techniques, Hinokami Kagura, tragic backstory, and complete character development through every arc."

### Featured Snippet
- 角色信息表(年龄/呼吸法/声优/首次登场)
- "How many Breathing Styles are there?" → 列表
- 篇章列表用有序列表

### 内链策略 — 剧情网络
- 角色页 → 该角色出现的篇章 + 相关角色(战友/敌人/师父)
- 呼吸法页 → 所有使用者
- 柱页 → 呼吸法 + 篇章(登场/战斗/牺牲)
- 鬼页 → 被谁打败 + 篇章
- 篇章页 → 登场角色 + 关键战斗
- 武器页 → 使用者 + 打造者
- 训练页 → 涉及的柱 + 篇章
- 地点页 → 相关篇章 + 登场角色
- 鬼杀队页 → 所有角色 + 等级关系
- 血鬼术页 → 对应鬼 + 战斗篇章

### 内容新鲜度
- 动画新季上线时更新相关内容
- 剧场版信息及时添加
- 标注内容覆盖范围(漫画完结/动画S5)

### 回访机制
- "Explore More Characters" → 按阵营引导(鬼杀队/柱/鬼)
- 篇章时间线导航
- 力量体系探索: 呼吸法 → 柱 → 篇章 学习路径
- 武器与血鬼术对抗体系: 日轮刀材质→锻造→变色→实战

### 富文本摘要
- Article Schema (详情页)
- ItemList Schema (角色索引/篇章索引)
- BreadcrumbList Schema

## 质量与UX标准

### 内容质量
- 角色页 ≥500字(简介+战斗风格+战绩+名场面)
- 呼吸法页: 所有招式列表(日文名+英文翻译+描述)
- 篇章页: 概述+关键战斗+角色发展
- 数据准确(漫画/动画官方设定)
- 禁止AI cliché

### 视觉质量 — 暗色底高标准
- 翠绿`#0F766E` + 近黑底`#0C0A09`，日系暗色风格
- **大图大尺寸**: 角色图 `object-cover`，暗色背景让角色色彩更突出
- **卡片横向布局**: 左侧图+右侧文字，整卡可点击
- 暗色底对比度: 正文`#D1D5DB` + 标题`#5EEAD4`通过WCAG AA
- **禁止图片阴影遮罩**

### UX设计
- 角色轮播 + Hashira展示网格 + Banner轮播≥6张(纯CSS)
- 面包屑 + 返回顶部 + 阅读进度条
- 移动端纯CSS汉堡菜单
- **呼吸法招式列表**: 序号+日文名+英文翻译，有序列表
- 鬼杀队等级: 等级徽章(CSS圆形badge)
- 血鬼术: 暗色信息框，红边框

### SEO
- Schema: Article + BreadcrumbList + Organization + WebSite + ItemList
- Meta/OG/Twitter/Canonical 完整
- 内部三角互链: 角色↔呼吸法↔篇章

### 广告位
- 3个/页(首页)，2个/详情页，纯自动广告，暗色广告用浅色容器包裹

### 性能 + 无障碍
- 预连接 + lazy loading + 零JS + 语义化HTML + Skip to content + 暗色focus亮outline

## 实现步骤

**执行前必读: `specs/MANDATORY_RULES.md`** — 所有强制规定必须在每个阶段逐条对照。

CF项目名: demonslayer-jycsd。

## 验收标准

```bash
ls demonslayer-site/characters/*.html | wc -l         # >= 15
ls demonslayer-site/hashira/*.html | wc -l            # >= 9
ls demonslayer-site/breathing-styles/*.html | wc -l   # >= 14
ls demonslayer-site/arcs/*.html | wc -l               # >= 12
ls demonslayer-site/demons/*.html | wc -l             # >= 12
ls demonslayer-site/weapons/*.html | wc -l            # >= 5
ls demonslayer-site/training/*.html | wc -l           # >= 5
ls demonslayer-site/locations/*.html | wc -l          # >= 5
ls demonslayer-site/corps/*.html | wc -l              # >= 5
ls demonslayer-site/blood-arts/*.html | wc -l         # >= 5
grep -c 'character-card' demonslayer-site/index.html  # >= 6
python shared/pre_commit_audit.py
python shared/check_portal_consistency.py
```

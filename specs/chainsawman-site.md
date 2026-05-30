# chainsawman-site — Chainsaw Man Wiki (电锯人)

---
MANDATORY_RULES_REF: specs/MANDATORY_RULES.md
STATUS: 本spec受MANDATORY_RULES.md约束，冲突时以总法为准。
---

## 基本信息

| 属性 | 值 |
|------|-----|
| 目录 | `chainsawman-site/` |
| 域名 | chainsawman.jycsd.com |
| 站点名称 | Chainsaw Man Database |
| 品牌色 | `#DC2626` (血红) + `#09090B` (黑底) |
| 类型 | 暗色底 anime 模板 (狂野风格) |
| 受众 | 全球动漫迷 |
| 月搜索量 | 800万+ |
| 模板类型 | anime 标准模板 (暗色) |
| 品牌 | Myers Media / Jordan Myers |

## 页面结构

```
chainsawman-site/
├── index.html / about.html / contact.html / privacy-policy.html
├── terms.html / cookie-policy.html / sitemap.xml
├── robots.txt / ads.txt / favicon.ico
├── images/
│   ├── default-og.jpg / logo.svg
│   ├── characters/         # 角色图 (~45张)
│   ├── devils/             # 恶魔图 (~24张)
│   └── banners/
├── characters/             # 15个角色页
├── characters/index.html   # 角色索引 (15个)
├── devils/                 # 12个恶魔页
├── devils/index.html       # 恶魔索引 (12个)
├── arcs/                   # 8个篇章
├── arcs/index.html         # 篇章索引 (8个)
├── organizations/          # 组织 (3页)
├── organizations/index.html # 组织索引
├── powers/                 # 能力 (4页)
├── powers/index.html       # 能力索引
├── weapons/                # 武器与工具 (5页)
├── weapons/index.html      # 武器索引
├── contracts/              # 契约与代价 (5页)
├── contracts/index.html    # 契约索引
├── world/                  # 世界观 (5页)
├── world/index.html        # 世界观索引
├── transformations/        # 变身与进化 (5页)
├── transformations/index.html # 变身索引
├── factions/               # 势力与政治 (5页)
├── factions/index.html     # 势力索引
└── index.html
```

总计约 **80页**。

> 参照站: aot-site (动漫站模板)。每个分类子目录必须有 index.html 作为该分类的全部条目列表页。首页 'View All' 按钮链接到对应 guides/*/index.html。

## 分类设计

### 1. Characters (角色, 15个)
- Denji / Makima / Aki Hayakawa / Power / Kobeni / Himeno / Kishibe / Reze / Quanxi / Santa Claus / Beam / Violence Fiend / Angel Devil / Asa Mitaka / Yoru
- 每页: 角色大图+信息表+能力+剧情线

### 2. Devils (恶魔, 12个)
- Chainsaw Devil (Pochita) / Gun Devil / Control Devil / Darkness Devil / Blood Devil / Fox Devil / Ghost Devil / Snake Devil / Curse Devil / Punishment Devil / Eternity Devil / Tomato Devil
- 每页: 恶魔图+契约+能力+出场

### 3. Arcs (篇章, 8个)
- Intro Arc / Bat Devil Arc / Eternity Devil Arc / Katana Man Arc / Bomb Girl Arc / International Assassins Arc / Gun Devil Arc / Control Devil Arc
- 每页: 篇章概述+关键战斗

### 4. Organizations (组织, 3页)
- Public Safety Devil Hunters / Yakuza / Soviet Union's Agents

### 5. Powers (能力, 4页)
- Devil Contracts / Hybrids / Fiends / Blood Manipulation

### 6. Weapons & Tools (武器与工具)
- Denji's Chainsaw Transformations: Arm chainsaw, leg chainsaw, full chainsaw form, hybrid trigger
- Devil Hunter Standard Weapons: Katanas, guns, axes, contract-based weapons explained
- Specialized Devil Hunting Tools: Aki's Curse Sword, Power's blood hammer, Kishibe's knives
- Weapon Devils as Allies: Chainsaw Devil (Pochita), Blood Devil contract mechanics
- Human-Produced Weapons: Gun pieces collection, gun manufacturing, anti-devil weaponry

### 7. Contracts & Sacrifices (契约与代价)
- Devil Contract Mechanics: Price determination, contract binding, how to negotiate with devils
- Notable Devil Contracts: Aki's multiple contracts detailed analysis, sacrifice hierarchy
- Contract Loopholes & Exploits: How characters bypass contracts, contract nullification cases
- The Cost of Power: Life force cost, body parts as sacrifice, lifespan reduction contracts
- Forced vs Voluntary Contracts: Makima's control contracts, gun devil forced contracts comparison

### 8. World & Setting (世界观)
- Chainsaw Man World History: Devil appearance in human world, gun devil incident, societal changes
- Devil Hunter Organizations by Country: Japan, Soviet Union, China, Germany, America approaches
- Hell in Chainsaw Man: Hell mechanics, devil reincarnation cycle, Darkness Devil domain
- Human-Devil Coexistence: Fiends, hybrids, devil rights, public perception of devils
- Timeline & Chronology: Complete Chainsaw Man timeline from Gun Devil appearance to Part 2

### 9. Transformations & Evolutions (变身与进化)
- Hybrid Transformation Mechanics: Trigger mechanisms, transformation stages, partial vs full hybrid
- Denji's Evolution: From basic chainsaw to full potential, power scaling through parts
- Fiend Forms vs True Devil Forms: Power comparison, appearance differences, control level
- Devil Reincarnation: Death in hell → reincarnation on earth, memory and appearance changes
- Power Awakening & Berserk States: Chainsaw Man true form, Power's blood devil awakening

### 10. Factions & Politics (势力与政治)
- Public Safety Devil Hunters: Division structure, Special Division 4, leadership hierarchy
- Yakuza & Criminal Underworld: Devil contracts with criminals, zombie devil incident
- International Assassins: Santa Claus, Quanxi, Tolka, and their national affiliations
- Gun Devil Factions: Gun devil fragments, different nations' gun devil pieces, Soviet Union agents
- Control Devil's Plan: Makima's goal, chainsaw man erasure power, world domination strategy

## 图片清单

| 类型 | 数量 | 来源 |
|------|------|------|
| 角色图 | 45 | pngwing.com |
| 恶魔图 | 24 | pngwing.com |
| Banner | 6 | 官方壁纸 |

## 首页区块

1. **Hero**: 血红暗底 + 轮播≥5张 (Denji/Makima/Power/Aki/Reze/Kishibe)
2. **Featured Characters**: 角色轮播
3. **Devil Encyclopedia**: 恶魔卡片网格
4. **Story Arcs**: 篇章导航
5. **Weapons Arsenal**: 武器卡片网格
6. **Contract Database**: 特色契约卡片
7. **World Exploration**: 世界观入口
8. **Transformations**: 进化图谱
9. **Faction Politics**: 势力概览
10. **AdSense**: 3个广告位

## CTR与流量增长策略

### 标题优化
- 角色页: "Denji - Chainsaw Man: Powers, Contracts & Complete Story Guide"
- 恶魔页: "Gun Devil Explained: Powers, History & Every Appearance"
- 含标志性元素(Chainsaw/Devil/Contract)增加辨识度

### Meta Description
- 角色定位+独特卖点
- 例: "Denji is the protagonist of Chainsaw Man, a devil hunter fused with Pochita the Chainsaw Devil. Learn his contracts, transformations, relationships, and full story arc."

### Featured Snippet
- 角色信息表
- 恶魔等级/能力列表
- 篇章时间线(列表)

### 内链策略
- 角色↔契约恶魔(双向)
- 恶魔↔被打败的篇章
- 角色↔所属组织
- 篇章↔登场角色+恶魔

### 内容新鲜度
- 动画Part 2/剧场版更新时同步
- 漫画新篇章发布后更新
- 标注内容范围(Part 1动画/Part 2漫画)

### 回访机制
- "Explore Devil Encyclopedia" → 恶魔等级引导
- 篇章连续阅读引导
- 角色关系图(概念，文字描述版)

### 富文本摘要
- Article Schema + ItemList Schema + BreadcrumbList Schema

## 质量与UX标准

### 内容质量
- 角色页 ≥500字(能力+契约+剧情线)
- 恶魔页 ≥400字(能力+契约条件+出场)
- 篇章页 ≥600字(概述+关键战斗+角色变化)
- 数据准确(漫画原作设定)
- 禁止AI cliché

### 视觉质量 — 狂野暗色风格
- 血红`#DC2626` + 黑底`#09090B`，狂野暴力美学
- 大图角色卡，`object-cover`
- 暗色对比度: 正文`#E5E5E5` + 标题`#F87171`(亮红)通过WCAG AA
- **禁止图片阴影遮罩**
- 恶魔契约: 警告框风格(红边框+暗红底)

### UX设计
- 角色轮播 + 恶魔图鉴网格 + Banner轮播≥5张(纯CSS)
- 面包屑 + 返回顶部 + 阅读进度条
- 移动端纯CSS汉堡菜单
- **恶魔排名**: 危险等级badge(SSS/SS/S/A/B)，CSS颜色编码
- 契约关系: 双向箭头连接线(CSS)
- 篇章时间线: 竖线+节点

### SEO
- Schema: Article + BreadcrumbList + Organization + WebSite
- Meta/OG/Twitter/Canonical 完整

### 广告位
- 3个首页/2个详情页，纯自动广告，暗色容器包裹

### 性能 + 无障碍
- 预连接 + lazy loading + 零JS + 语义化HTML + Skip to content

## 实现步骤

**执行前必读: `specs/MANDATORY_RULES.md`** — 所有强制规定必须在每个阶段逐条对照。

CF项目名: chainsawman-jycsd。

## 验收标准

```bash
ls chainsawman-site/characters/*.html | wc -l           # >= 15
ls chainsawman-site/devils/*.html | wc -l               # >= 12
ls chainsawman-site/arcs/*.html | wc -l                 # >= 8
ls chainsawman-site/organizations/*.html | wc -l        # >= 3
ls chainsawman-site/powers/*.html | wc -l               # >= 4
ls chainsawman-site/weapons/*.html | wc -l              # >= 5
ls chainsawman-site/contracts/*.html | wc -l            # >= 5
ls chainsawman-site/world/*.html | wc -l                # >= 5
ls chainsawman-site/transformations/*.html | wc -l      # >= 5
ls chainsawman-site/factions/*.html | wc -l             # >= 5
python shared/pre_commit_audit.py
python shared/check_portal_consistency.py
```

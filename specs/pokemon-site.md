# pokemon-site — Pokemon Wiki (宝可梦)

---
MANDATORY_RULES_REF: specs/MANDATORY_RULES.md
STATUS: 本spec受MANDATORY_RULES.md约束，冲突时以总法为准。
---

## 基本信息

| 属性 | 值 |
|------|-----|
| 目录 | `pokemon-site/` |
| 域名 | pokemon.jycsd.com |
| 站点名称 | PokeDex Guide |
| 品牌色 | `#FACC15` (黄) + `#DC2626` (红) + 白底 |
| 类型 | 明亮底 game 模板 |
| 受众 | 全年龄 |
| 月搜索量 | 5000万+ |
| 模板类型 | game 标准模板 |
| 品牌 | Myers Media / Jordan Myers |

## 页面结构

```
pokemon-site/
├── index.html              # 首页
├── about.html / contact.html / privacy-policy.html
├── terms.html / cookie-policy.html / sitemap.xml
├── robots.txt / ads.txt / favicon.ico
├── images/
│   ├── default-og.jpg / logo.svg
│   ├── pokemon/            # 50只宝可梦图片 (每只2-3张, ~120张)
│   ├── types/              # 18属性图标
│   └── banners/            # 轮播横幅 6-8张
├── pokemon/                # 50个宝可梦详情页
├── pokemon/index.html      # 宝可梦图鉴索引 (50只)
├── types/                  # 18属性索引页 + 属性详情页
├── types/index.html        # 18属性索引
├── regions/                # 9代地区页
├── regions/index.html      # 9代地区索引
├── competitive/            # 对战指南 (5页)
├── competitive/index.html  # 对战指南索引
├── evolution/              # 进化系统 (3页)
├── evolution/index.html    # 进化链索引
├── breeding/               # 培育指南 (5页)
├── breeding/index.html     # 培育指南索引
├── shiny/                  # 闪光狩猎 (5页)
├── shiny/index.html        # 闪光狩猎索引
├── items/                  # 道具与携带物 (5页)
├── items/index.html        # 道具与携带物索引
├── nuzlocke/               # Nuzlocke挑战 (5页)
├── nuzlocke/index.html     # Nuzlocke挑战索引
├── tcg/                    # 卡牌与媒体 (5页)
└── tcg/index.html          # 卡牌与媒体索引
```

总计约 **90页**。

> 参照站: naruto-site (游戏站模板)。每个分类子目录必须有 index.html 作为该分类的全部条目列表页。首页 'View All' 按钮链接到对应 guides/*/index.html。

## 精选50只顶流宝可梦

按代/人气/搜索量筛选:

### Gen 1 (Kanto) — 15只
Pikachu, Charizard, Mewtwo, Eevee, Gengar, Dragonite, Snorlax, Gyarados, Mew, Bulbasaur, Squirtle, Jigglypuff, Psyduck, Arcanine, Machamp

### Gen 2 (Johto) — 7只
Tyranitar, Lugia, Ho-Oh, Umbreon, Scizor, Ampharos, Typhlosion

### Gen 3 (Hoenn) — 7只
Rayquaza, Blaziken, Gardevoir, Metagross, Salamence, Kyogre, Absol

### Gen 4 (Sinnoh) — 6只
Lucario, Garchomp, Darkrai, Giratina, Infernape, Togekiss

### Gen 5 (Unova) — 4只
Zekrom, Hydreigon, Chandelure, Zoroark

### Gen 6 (Kalos) — 3只
Greninja, Aegislash, Sylveon

### Gen 7 (Alola) — 3只
Mimikyu, Lycanroc, Incineroar

### Gen 8 (Galar) — 3只
Dragapult, Zacian, Toxtricity

### Gen 9 (Paldea) — 2只
Koraidon, Ceruledge

## 分类设计

### 1. Pokedex (宝可梦图鉴)
- 50个独立页面，每页结构:
  - 宝可梦名称/编号/属性/分类
  - 2-3张大图 (官方立绘+游戏截图+动画截图)
  - 基础信息表 (身高/体重/特性)
  - 进化链
  - 对战定位
- 图鉴索引页: 卡片网格 (按代分组)

### 2. Types (属性系统, 18种)
- 属性索引页: 18属性卡片网格
- 每属性一个详情页: 克制关系表 + 代表宝可梦列表
- 18属性: Normal/Fire/Water/Electric/Grass/Ice/Fighting/Poison/Ground/Flying/Psychic/Bug/Rock/Ghost/Dragon/Dark/Steel/Fairy

### 3. Regions (地区, 9代)
- 9个地区索引页: 每页地图+道馆列表+代表宝可梦
- Kanto → Johto → Hoenn → Sinnoh → Unova → Kalos → Alola → Galar → Paldea

### 4. Competitive (对战)
- 5页: 对战基础/IVs&EVs/常见队伍配置/属性联防/规则赛季更新

### 5. Evolution (进化)
- 3页: 进化机制总览/特殊进化方法/Eevee全进化分支

### 6. Breeding Guide (培育指南)
- Pokemon Breeding Basics: Day Care, egg groups, egg moves explained
- IV Breeding Complete Guide: Destiny Knot, Everstone, chain breeding methods
- Nature & Ability Breeding: Synchronize, Ability Capsule vs Patch, Hidden Ability breeding
- Egg Move Chains: Cross-breeding for competitive moves, notable egg move combos
- Shiny Breeding Methods: Masuda Method, Shiny Charm stacking, odds comparison

### 7. Shiny Hunting (闪光狩猎)
- Shiny Pokemon Complete Guide: Base odds, Shiny Charm, encounter methods comparison
- Masuda Method Deep Dive: Breeding for shinies step by step, egg cycles by species
- Wild Shiny Hunting Methods: SOS chaining, DexNav, Pokeradar, Chain Fishing, horde encounters
- Legendary & Mythical Shiny Hunting: Soft resetting, Dynamax Adventures, Ramanas Park
- Sandwich & Outbreak Method (SV): Mass outbreaks, sparkling power sandwiches, isolated encounters

### 8. Items & Held Items (道具与携带物)
- Competitive Held Items Guide: Choice items, Life Orb, Focus Sash, Assault Vest, Leftovers explained
- Type Enhancement Items: Plates, type gems, type-boosting held items complete list
- Evolution Items: All evolution stones, trade items, location-specific evolution items
- Battle Items & Consumables: X items, Potions hierarchy, status healers, Pokeball types guide
- Key Items & TM Locations: Notable key items across generations, must-have TM farming spots

### 9. Nuzlocke Challenge (Nuzlocke挑战)
- Nuzlocke Rules & Variants: Standard rules, Hardcore, Wedlocke, Soul Link, Randomizer explained
- Best Starter Pokemon for Nuzlocke: Generation-by-generation starter tier list and reasoning
- Nuzlocke Encounter Routing: Route planning, repel manipulation, guaranteed encounters
- Gym Leader & Elite Four Counters: How to prepare for every major fight without losing Pokemon
- Nuzlocke Tips & Strategies: Grinding safely, death prevention, backup team building

### 10. Pokemon TCG & Media (卡牌与媒体)
- Pokemon TCG Basics for Beginners: Card types, energy, evolution in TCG, how to build a deck
- Most Valuable Pokemon Cards: Charizard 1st Edition, Illustrator Pikachu, modern chase cards
- Pokemon Anime Guide: Series watch order, movies, specials, where to start
- Pokemon Games Timeline: Every main series game from Red/Blue to Scarlet/Violet
- Pokemon GO Integration: Transferring, Home connectivity, GO-exclusive Pokemon

## 图片清单

| 类型 | 数量 | 来源 |
|------|------|------|
| 宝可梦角色图 | ~120 (50只×2-3) | pngwing.com 下载 + 官方素材 |
| 属性图标 | 18 | 自制SVG或官方素材 |
| Banner图 | 8 | 官方壁纸+高清截图 |
| OG默认图 | 1 | 品牌色底+logo |

## 首页区块

1. **Hero Banner**: 轮播≥5张 (Pikachu/Charizard/Mewtwo/Lucario/Greninja/Garchomp/Rayquaza/龙系精选)
2. **Featured Pokemon**: 横排角色轮播 (4-6张/行，鼠标拖动，悬停暂停)
3. **Type Quick Nav**: 18属性图标网格
4. **Region Explorer**: 9代地区卡片
5. **Latest Guides**: 对战/进化/培育/闪光狩猎/道具/Nuzlocke/卡牌最新内容
6. **Breeding Quick Start**: 培育入门速查 (蛋组/遗传/个体值)
7. **Shiny Hunting Methods**: 各世代闪光狩猎方法对比
8. **Item Encyclopedia**: 进化石/对战道具/携带物分类速查
9. **AdSense**: 3个广告位

## 内容大纲

### 宝可梦详情页模板
```
- 顶部: 大图 (角色渲染或官方立绘)
- 右侧: 名称 + 编号 + 属性标签 + 分类
- 信息表: Height / Weight / Abilities / Base Stats
- 进化链: 箭头图或卡片链
- 对战分析: 常见配招 / 道具 / 定位
- "Related Pokemon"横向推荐
```

## CTR与流量增长策略

### 标题优化
- 宝可梦页: "Charizard - Complete Guide: Stats, Evolution & Best Moveset"
- 格式: `[Pokemon Name] - [核心卖点]: [Stats/Evolution/Competitive]`
- 属性页: "Fire Type Pokemon: Complete List, Strengths & Weaknesses"
- 含具体游戏数据增加专业感和点击欲
- 长度≤60字符

### Meta Description
- 每个宝可梦页含: 属性+进化链+对战定位
- 例: "Charizard is a Fire/Flying type Pokemon from Generation 1. Learn its base stats, evolution chain (Charmander→Charmeleon→Charizard), best moveset, and competitive strategy."

### Featured Snippet
- 宝可梦信息表直接进table snippet
- "What is Charizard weak against?" → 40-60字直接回答
- 属性克制关系用表格(18x18)
- 宝可梦列表用有序列表

### 内链策略 — 搜索流量闭环
- 每个宝可梦页链接: 进化链上下级 + 同属性宝可梦 + 同地区宝可梦
- 属性页→该属性所有宝可梦(双向链接)
- 对战指南→具体宝可梦推荐
- 孤岛页面零容忍

### 内容新鲜度
- 新代/新游戏发布时更新相关内容
- 对战meta变化时更新推荐配置
- 标注 "Updated for [Game Version]"

### 回访机制
- "Explore More Pokemon" → 下一个宝可梦引导
- 宝可梦图鉴编号导航(← #005 #006 #007 →)
- "Build Your Team" 互动概念(收藏/对比)

### 富文本摘要
- Article Schema (详情页)
- ItemList Schema (列表/索引页)
- BreadcrumbList Schema
- Table Schema (属性克制表/宝可梦对比)

## 质量与UX标准

### 内容质量
- 每个宝可梦详情页 ≥600字实质性内容(不堆砌废话)
- 页面结构: 大图 → 信息表 → 简介 → 对战定位 → 进化链 → 相关宝可梦
- 所有数据(属性/身高/体重/特性/进化等级)必须准确，从官方来源验证
- 每页显示 "Last updated: YYYY-MM-DD"
- 禁止AI cliché

### 视觉质量 — 游戏站最高标准
- **大图大尺寸**: 宝可梦图片 `object-cover` 填满容器，宽高一致，禁止白色背景
- **卡片横向布局**: 左侧图(40%) + 右侧文字(60%)，整卡`<a>`可点击
- 黄色`#FACC15` + 红色`#DC2626` 品牌色，明亮活泼
- 图片lazy loading + 描述性alt文本 (如 "Charizard official artwork - Fire/Flying type Pokemon")
- **禁止图片阴影遮罩**
- 属性标签: 彩色标签(badge)，每个属性有专属颜色

### UX设计
- **角色轮播**: 首页横向循环滚动(CSS animation) + 鼠标拖动，4-6张/行，悬停暂停
- **每版块 "View All →"**: 首页精选4-6条，链接到分类索引页展示全部
- **Banner轮播 ≥6张**: 纯CSS animation，非JS
- 面包屑 + 返回顶部 + 阅读进度条
- 移动端纯CSS汉堡菜单
- 属性克制表: 18x18交互式表格(桌面端)，移动端简化
- 进化链: 箭头卡片链，每节点可点击

### SEO
- Schema: Article(详情页) + BreadcrumbList + Organization + WebSite + ItemList(索引页)
- Meta 150-160字符，含宝可梦名称+属性
- OG图片: 每个宝可梦页面用该宝可梦专属OG图
- 内部链接: 每个宝可梦页链接相关进化/同属性宝可梦

### 广告位
- 首页3个，详情页2个(信息表下方+进化链前)，纯自动广告，禁止手动广告位

### 性能
- 预连接 + lazy loading + 零JS + 语义化HTML + Skip to content

### 无障碍
- 属性标签: 颜色+文字(+图标)，不只用颜色区分
- 所有图片alt文本含宝可梦名称

## 实现步骤

**执行前必读: `specs/MANDATORY_RULES.md`** — 所有强制规定必须在每个阶段逐条对照。

1. **规划书** → 本spec + 确认50只名单
2. **模板** → 基于game模板(明亮底)，品牌色黄+红
3. **收集图片** → pngwing.com 批量下载50只宝可梦图片，每只2-3张
4. **豆包验证** → 每张图片验证角色匹配
5. **PIL压缩** → max_width=1200, quality=85
6. **填充内容** → 生成所有页面 (90页)
7. **本地验证** → pre_commit_audit + portal + quality
8. **CF Pages** → pokemon-jycsd
9. **部署** → wrangler deploy + 线上验证

## 验收标准

```bash
ls pokemon-site/pokemon/*.html | wc -l             # >= 50
ls pokemon-site/types/*.html | wc -l               # >= 19 (index+18)
ls pokemon-site/regions/*.html | wc -l             # >= 9
ls pokemon-site/competitive/*.html | wc -l         # >= 6 (index+5)
ls pokemon-site/evolution/*.html | wc -l           # >= 4 (index+3)
ls pokemon-site/breeding/*.html | wc -l            # >= 6 (index+5)
ls pokemon-site/shiny/*.html | wc -l               # >= 6 (index+5)
ls pokemon-site/items/*.html | wc -l               # >= 6 (index+5)
ls pokemon-site/nuzlocke/*.html | wc -l            # >= 6 (index+5)
ls pokemon-site/tcg/*.html | wc -l                 # >= 6 (index+5)
ls pokemon-site/images/pokemon/*.jpg | wc -l       # >= 100
grep -c 'character-card' pokemon-site/index.html   # >= 6
python shared/pre_commit_audit.py                    # 0 ERROR
python shared/check_portal_consistency.py            # OK
python shared/health_check_daily.py --quality        # ALL OK
```

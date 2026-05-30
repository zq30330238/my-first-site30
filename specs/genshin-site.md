# genshin-site — Genshin Impact Wiki (原神)

---
MANDATORY_RULES_REF: specs/MANDATORY_RULES.md
STATUS: 本spec受MANDATORY_RULES.md约束，冲突时以总法为准。
---

## 基本信息

| 属性 | 值 |
|------|-----|
| 目录 | `genshin-site/` |
| 域名 | genshin.jycsd.com |
| 站点名称 | Teyvat Archive |
| 品牌色 | `#6366F1` (靛) + `#0F172A` (深蓝黑底) |
| 类型 | 暗色底 game 模板 |
| 受众 | 全球/年轻玩家 |
| 月搜索量 | 4000万+ |
| 模板类型 | game 标准模板 (暗色) |
| 品牌 | Myers Media / Jordan Myers |

## 页面结构

```
genshin-site/
├── index.html / about.html / contact.html / privacy-policy.html
├── terms.html / cookie-policy.html / sitemap.xml
├── robots.txt / ads.txt / favicon.ico
├── images/
│   ├── default-og.jpg / logo.svg
│   ├── characters/         # 30角色图 (~90张)
│   ├── elements/           # 7元素图标
│   ├── regions/            # 7地区背景图
│   └── banners/            # 轮播横幅
├── characters/             # 30个角色详情页
├── characters/index.html   # 角色索引 (30个)
├── elements/               # 7元素页 + 元素反应页
├── elements/index.html     # 7元素索引
├── regions/                # 7地区页
├── regions/index.html      # 7地区索引
├── weapons/                # 武器类型页 (5页)
├── weapons/index.html      # 武器索引
├── artifacts/              # 圣遗物页 (5页)
├── artifacts/index.html    # 圣遗物索引
├── team-comps/             # 队伍搭配 (6页)
├── team-comps/index.html   # 队伍搭配索引
├── spiral-abyss/           # 深境螺旋 (5页)
├── spiral-abyss/index.html # 深境螺旋索引
├── materials/              # 材料刷取 (5页)
├── materials/index.html    # 材料刷取索引
├── lore/                   # 世界观故事 (5页)
├── lore/index.html         # 世界观故事索引
├── events/                 # 活动与版本 (5页)
├── events/index.html       # 活动与版本索引
└── index.html
```

总计约 **100页**。

> 参照站: naruto-site (游戏站模板)。每个分类子目录必须有 index.html 作为该分类的全部条目列表页。首页 'View All' 按钮链接到对应 guides/*/index.html。

## 精选30个核心角色

**5星限定 (20个)**:
Raiden Shogun, Zhongli, Nahida, Furina, Venti, Kazuha, Hu Tao, Ganyu, Ayaka, Xiao, Yelan, Tartaglia, Alhaitham, Neuvillette, Arlecchino, Wriothesley, Wanderer, Nilou, Kokomi, Yoimiya

**常驻5星 (5个)**:
Diluc, Jean, Mona, Keqing, Tighnari

**热门4星 (5个)**:
Bennett, Xingqiu, Xiangling, Fischl, Sucrose

## 分类设计

### 1. Characters (角色, 30个)
- 每角色独立页: 名称/星级/元素/武器类型/地区
- 2-3张大图 (官方立绘+游戏截图)
- 角色简介/技能概述/配队建议/圣遗物推荐
- 横向卡片布局 (左侧图右侧文字)

### 2. Elements (元素系统)
- **7元素页**: Pyro/Hydro/Anemo/Electro/Dendro/Cryo/Geo
- 每页: 元素机制+代表角色+元素反应表
- **1个元素反应总览页**: 所有反应组合+倍率

### 3. Regions (地区, 7国)
- Mondstadt / Liyue / Inazuma / Sumeru / Fontaine / Natlan / Snezhnaya
- 每页: 世界观+地标+代表角色+剧情要点

### 4. Weapons (武器)
- 5页: Sword/Claymore/Polearm/Bow/Catalyst
- 每页: 武器类型特点+推荐武器列表+适用角色

### 5. Artifacts (圣遗物)
- 5页: 通用圣遗物套装+各角色推荐+主副属性选择+强化策略

### 6. Team Compositions (队伍搭配)
- **Popular Team Archetypes**: National/Rational/Hyperbloom/Vape/Melt/Freeze/Mono/Quickbloom/Burgeon teams explained
- **Raiden National & Variants**: Raiden/Xingqiu/Xiangling/Bennett rotations and builds
- **Dendro Teams Deep Dive**: Hyperbloom/Bloom/Burgeon team building with Nahida cores
- **Freeze & Morgana**: Freeze team mechanics, Ganyu/Mona/Venti compositions
- **Double Hydro & Vape**: Hu Tao/Yelan/Xingqiu vape teams, Yoimiya alternatives
- **Hypercarry & Mono Teams**: Xiao/Wanderer/Itto hypercarry builds and supports

### 7. Spiral Abyss (深境螺旋)
- **Spiral Abyss Complete Overview**: Reset schedule, floor breakdown, Ley Line Disorders explained
- **Floor 12 Guide**: Latest Floor 12 chamber strategies, enemy lineups, recommended teams
- **Floor 11 Guide**: Chamber analysis, debuff management, team recommendations
- **Spiral Abyss Meta Analysis**: Most used characters, team archetypes, usage rate trends
- **Budget & F2P Abyss Clearing**: Low-cost teams, 4-star only strategies, resource management

### 8. Materials & Farming (材料刷取)
- **Ascension Material Farming Routes**: Regional specialties, elite enemy routes, daily farming path
- **Talent Book Domain Guide**: Weekly schedule, domain overview, resin efficiency
- **Weapon Material Domain Guide**: Weekly rotation, which weapons need which materials
- **Boss Material Farming**: World boss and weekly boss resin costs, drop rates
- **Artifact Farming Efficiency**: Domain resin efficiency, strongbox recommendations, artifact XP routes

### 9. Lore & Story (世界观故事)
- **Teyvat World Lore**: Archon War, Celestia, Abyss Order, Khaenri'ah explained
- **Archon Quest Summary**: Prologue through Chapter V story recap
- **Character Story Quests**: Notable story quests and lore drops for top characters
- **World Quests Worth Doing**: Aranyaka, Golden Slumber, Sakura Cleansing, and other major world quests
- **Hidden Lore & Theories**: Istaroth, Descenders, Fake Sky, Hexenzirkel, and major fan theories

### 10. Events & Version Updates (活动与版本)
- **Version History Overview**: 1.0 through 5.x major feature additions and changes
- **Annual Flagship Events**: Lantern Rite, Summer events, Windblume, and other recurring events
- **Event Minigame Types**: Combat events, exploration events, rhythm games, tower defense, trading card
- **Spiral Abyss & Imaginarium Theater**: Endgame mode differences, rewards, strategies
- **Upcoming Content & Leaks**: Banner speculation, new character rumors, future region teasers

## 图片清单

| 类型 | 数量 | 来源 |
|------|------|------|
| 角色图 | ~90 (30角色×3) | pngwing.com + 官方素材 |
| 元素图标 | 7 | 官方素材/自制SVG |
| 地区图 | 7 | 官方壁纸/截图 |
| Banner | 8 | 官方壁纸 |

## 首页区块

1. **Hero Banner**: 轮播≥6张 (Raiden/Zhongli/Nahida/Furini/Kazuha/Hu Tao/Arlecchino/Neuvillette)
2. **Featured Characters**: 角色轮播 (4-6/行)
3. **Element Quick Nav**: 7元素图标网格
4. **Region Explorer**: 7地区卡片
5. **Latest Guides**: 武器/圣遗物精选
6. **Team Compositions**: Featured team archetypes with 4-character cards
7. **Spiral Abyss Tips**: Current floor tips and recommended teams
8. **Materials Farming Guide**: Quick links to farming routes
9. **Lore Highlights**: Featured world lore articles
10. **Latest Version Updates**: Current version event and banner info
11. **AdSense**: 3个广告位

## CTR与流量增长策略

### 标题优化
- 角色页: "Raiden Shogun Guide - Best Build, Team Comps & Artifacts"
- 格式: `[Character Name] - [Best Build/Team/Artifacts]`
- 元素页: "Hydro Element Guide: All Characters, Reactions & Resonance"
- 含游戏术语(Build/Team Comp/Artifact)吸引玩家
- 长度≤60字符

### Meta Description
- 每角色: 星级+元素+武器+核心定位一句话
- 例: "Raiden Shogun is a 5-star Electro Polearm character. Discover her best build, artifact sets (Emblem of Severed Fate), team compositions, and talent priority."

### Featured Snippet
- 角色信息表进table snippet
- "Best team for Raiden Shogun?" → 40-60字 + 列表
- 元素反应表进table snippet
- 圣遗物推荐用有序列表

### 内链策略 — 三角互链闭环
- 角色页 → 推荐队友角色页 + 使用元素页 + 所属地区页
- 元素页 → 该元素所有角色
- 地区页 → 该地区所有角色
- 武器页 → 适用角色列表
- 圣遗物页 → 推荐角色列表
- 队伍搭配页 → 组成角色详情页 + 相关元素/武器页
- 深境螺旋页 → 推荐配队链接
- 材料刷取页 → 相关角色/武器/圣遗物链接

### 内容新鲜度
- 新角色发布 → 48小时内上线角色页
- 版本更新时更新Build推荐
- 标注 "Updated for Version X.X"

### 回访机制
- "Explore More Characters" → 元素/地区相关角色引导
- 配队推荐中的队友链接 → 引导浏览多个角色页
- 角色对比功能(表格形式，无JS)

### 富文本摘要
- Article Schema (详情页)
- ItemList Schema (角色索引)
- BreadcrumbList Schema

## 质量与UX标准

### 内容质量
- 每个角色详情页 ≥600字实质性内容
- 页面结构: 大图 → 信息表(星级/元素/武器/地区) → 角色简介 → 技能概述 → 配队建议 → 圣遗物推荐
- 元素反应、圣遗物数据必须准确
- 每页 "Last updated: YYYY-MM-DD"
- 禁止AI cliché

### 视觉质量 — 暗色底高标准
- **大图大尺寸**: 角色立绘 `object-cover`，暗色背景衬托色彩
- **卡片横向布局**: 左侧图(40%) + 右侧文字(60%)，整卡`<a>`可点击
- 靛色`#6366F1` + 深蓝黑底`#0F172A`，元素色点缀
- 图片lazy loading + 描述性alt
- **禁止图片阴影遮罩**
- 元素标签: 7元素7色(badge)，一目了然
- 星级: ★★★★★ (CSS黄色星)，直观显示稀有度

### UX设计
- 角色轮播 + View All → + Banner轮播≥6张(纯CSS)
- 面包屑 + 返回顶部 + 阅读进度条
- 移动端纯CSS汉堡菜单
- **元素反应表**: 交互式表格，横向竖向交叉
- 配队展示: 4角色卡片横排，每角色小头像+定位标签(Main DPS/Support/Healer)
- 圣遗物推荐: 套装卡片，含2件/4件效果

### SEO
- Schema: Article + BreadcrumbList + Organization + WebSite + ItemList
- Meta + OG + Twitter + Canonical 完整
- 内部链接: 角色→元素→地区三角互链

### 广告位
- 首页3个，角色页2个，纯自动广告，禁止手动广告位
- 暗色底广告: 浅色卡片容器包裹

### 性能 + 无障碍
- 预连接 + lazy loading + 零JS + 语义化HTML + Skip to content
- 暗色底focus用亮色outline

## 实现步骤

**执行前必读: `specs/MANDATORY_RULES.md`** — 所有强制规定必须在每个阶段逐条对照。

1-9步流程。CF项目名: genshin-jycsd。
**注**: 最大单站，角色数多、分类多，建议分2批Agent并行生成 (角色15+15)。

## 验收标准

```bash
ls genshin-site/characters/*.html | wc -l           # >= 30
ls genshin-site/elements/*.html | wc -l             # >= 8
ls genshin-site/regions/*.html | wc -l              # >= 7
ls genshin-site/images/characters/*.jpg | wc -l     # >= 90
grep -c 'character-card' genshin-site/index.html    # >= 6
ls genshin-site/team-comps/*.html | wc -l           # >= 6
ls genshin-site/spiral-abyss/*.html | wc -l         # >= 5
ls genshin-site/materials/*.html | wc -l            # >= 5
ls genshin-site/lore/*.html | wc -l                 # >= 5
ls genshin-site/events/*.html | wc -l               # >= 5
python shared/pre_commit_audit.py
python shared/check_portal_consistency.py
python shared/health_check_daily.py --quality
```

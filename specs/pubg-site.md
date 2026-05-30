# pubg-site — PUBG Guide (绝地求生)

---
MANDATORY_RULES_REF: specs/MANDATORY_RULES.md
STATUS: 本spec受MANDATORY_RULES.md约束，冲突时以总法为准。
---

## 基本信息

| 属性 | 值 |
|------|-----|
| 目录 | `pubg-site/` |
| 域名 | pubg.jycsd.com |
| 站点名称 | Battlegrounds Guide |
| 品牌色 | `#F97316` (橙) + `#171717` (深灰底) |
| 类型 | 暗色底 game 模板 |
| 受众 | 全球/男性玩家 |
| 月搜索量 | 1500万+ |
| 模板类型 | game 标准模板 (暗色) |
| 品牌 | Myers Media / Jordan Myers |

## 页面结构

```
pubg-site/
├── index.html / about.html / contact.html / privacy-policy.html
├── terms.html / cookie-policy.html / sitemap.xml
├── robots.txt / ads.txt / favicon.ico
├── images/
│   ├── default-og.jpg / logo.svg
│   ├── weapons/            # 武器图
│   ├── maps/               # 地图
│   └── banners/
├── weapons/                # 武器库 (6页)
├── weapons/index.html      # 武器库索引
├── maps/                   # 地图降落地 (6页)
├── maps/index.html         # 地图索引
├── tactics/                # 战术指南 (5页)
├── tactics/index.html      # 战术指南索引
├── vehicles/               # 载具 (4页)
├── vehicles/index.html     # 载具指南索引
├── updates/                # 更新补丁 (4页)
├── updates/index.html      # 更新补丁索引
├── ranked/                 # 排位模式 (5页)
├── ranked/index.html       # 排位模式索引
├── crates/                 # 空投武器与特殊物品 (5页)
├── crates/index.html       # 空投武器索引
├── roles/                  # 团队角色与沟通 (5页)
├── roles/index.html        # 团队角色索引
├── survival/               # 生存与转移策略 (5页)
├── survival/index.html     # 生存策略索引
├── settings/               # 设置与职业配置 (5页)
├── settings/index.html     # 设置配置索引
└── index.html
```

总计约 **60页**。

> 参照站: naruto-site (游戏站模板)。每个分类子目录必须有 index.html 作为该分类的全部条目列表页。首页 'View All' 按钮链接到对应 guides/*/index.html。

## 分类设计

### 1. Weapons (武器)
- 6页: AR(突击步枪)/SR(狙击)/SMG(冲锋枪)/Shotgun(霰弹)/Pistol(手枪)/Throwables(投掷物)
- 每页: 武器列表+伤害数据+配件推荐

### 2. Maps (地图)
- 6页: Erangel/Miramar/Sanrok/Taego/Vikendi/Deston
- 每页: 地图标注(降落地/车辆/物资点)+策略

### 3. Tactics (战术)
- 5页: 降落策略/圈边打法/攻楼技巧/团队配合/单人四排

### 4. Vehicle Guide (载具)
- 4页: 陆地载具/水上载具/滑翔机/载具战术

### 5. Update Patch (更新)
- 4页: 最新补丁/武器平衡/地图更新/赛季内容

### 6. Ranked Mode (排位模式)
- PUBG Ranked Complete Guide: Rank tiers, RP system, placement vs kills weighting
- Ranked Map Rotation: Current map pool, best strategies per map
- How to Climb in Ranked: Solo vs Squad approach, survival vs aggression balance
- Ranked Meta Analysis: Current weapon meta, drop spot meta, rotation patterns
- Ranked Rewards & Seasons: Seasonal rewards, how to earn parachute skins and medals

### 7. Crate Weapons & Special Items (空投武器)
- All Crate Weapons Guide: AWM, MK14, P90, Groza, MG3, Lynx AMR, Famas full comparison
- Crate Weapon Tier List: Which crate weapons are worth the risk
- Flare Gun & BRDM Guide: How to use flare guns, BRDM vs armored UAZ comparison
- Special Items & Consumables: Blue Chip Detector, EMT Gear, Tactical Pack, Drone, Spotter Scope
- Secret Room & Loot Cache Locations: Taego secret rooms, Deston security keys, Vikendi vaults

### 8. Team Roles & Communication (团队角色)
- Squad Roles Explained: IGL (In-Game Leader), Fragger, Support, Scout responsibilities
- In-Game Leader Guide: Rotation calls, engagement decisions, team management skills
- Effective Comms & Callouts: Ping system, compass callouts, enemy position descriptions
- Team Fight Coordination: Flanking, crossfire setup, smoke usage, revive tactics
- Clutch Situations Guide: 1v2, 1v3, 1v4 strategies, staying calm, utility usage

### 9. Survival & Rotation Strategy (生存与转移)
- Zone & Circle Management: Blue zone damage by phase, rotation timing, vehicle necessity
- Hot Drop vs Safe Start: Risk/reward analysis, which strategy fits your playstyle
- Compound Clearing Guide: How to safely clear buildings, room-by-room tactics
- Bridge Camping & Ambushes: Bridge camp setups, counter-play, map-specific bridges
- Late Game Positioning: Final circle positioning, snake vs aggressive, terrain advantage

### 10. Settings & Pro Configs (设置与职业配置)
- Best Graphics Settings for PUBG: Visibility, FPS, render distance optimization for competitive advantage
- Sensitivity & DPI Guide: Pro player sensitivities, ADS vs scope settings, finding your sweet spot
- Keybinds & Controller Layout: Optimal keybind setups, controller button mapping for console
- Audio Settings for Footsteps: HRTF, sound normalization, headphone recommendations
- Pro Player Config Database: Notable pro players' full settings, gear, and setups

## 图片清单

| 类型 | 数量 | 来源 |
|------|------|------|
| 武器渲染图 | ~30 | PUBG官方素材/wiki |
| 地图标注图 | 6 | 游戏截图+标注 |
| Banner | 8 | 官方壁纸 |

## 首页区块

1. **Hero**: 暗色底+橙色accent + 轮播≥5张
2. **Weapon Spotlight**: 热门武器快速导航
3. **Map Explorer**: 地图卡片网格
4. **Ranked Mode**: 排位模式导航卡
5. **Crate Weapons**: 空投武器特色卡
6. **Latest Updates**: 最新补丁内容
7. **AdSense**: 3个广告位

## CTR与流量增长策略

### 标题优化
- 武器页: "M416 Guide - Best Loadout, Recoil Control & Damage Stats"
- 地图页: "Erangel Map Guide - Best Drop Spots, Loot Routes & Vehicle Spawns"
- 格式: `[Weapon/Map Name] - [核心数据]: [Best/Build/Stats]`

### Meta Description
- 具体游戏数据 + CTA
- 例: "Master the M416 with our complete loadout guide. Learn recoil patterns, best attachments, damage stats, and pro player setups."

### Featured Snippet
- 武器数据表进table snippet
- "Best drop spot in Erangel?" → 列表
- 战术步骤用HowTo Schema

### 内链策略
- 武器页 → 同类武器对比 + 推荐地图
- 地图页 → 推荐武器 + 战术
- 战术页 → 具体武器/地图页
- 更新补丁 → 受影响武器/地图
- 排位页 → 热门武器 + 推荐地图
- 空投武器页 → 地图降落地 + 战术策略
- 团队角色页 → 战术指南 + 生存策略

### 内容新鲜度
- 武器数据随游戏补丁更新
- 标注 "Updated for Patch 32.x"
- 赛季内容及时更新

### 回访机制
- "Explore More Weapons" → 同类型武器引导
- 武器对比表格(用户想比较多个武器)
- 战术学习路径

### 富文本摘要
- Article Schema + 数据表Schema
- BreadcrumbList Schema

## 质量与UX标准

### 内容质量
- 武器页: 每武器 ≥150字描述 + 伤害数据表 + 配件推荐
- 地图页: 标注点 ≥8处 + 策略说明
- 战术页: ≥800字，含具体场景和步骤
- 所有游戏数据(DPS/射速/伤害)需准确
- 禁止AI cliché

### 视觉质量 — 军事暗色风格
- 橙色`#F97316` + 深灰底`#171717`，军事风
- 武器图: 高清渲染图，`object-cover`
- 地图: 鸟瞰图 + 标注点叠加层
- 暗色底对比度: 正文`#E5E7EB` + 标题`#FB923C`通过WCAG AA
- **禁止图片阴影遮罩**

### UX设计
- Banner轮播≥5张(纯CSS)
- 面包屑 + 返回顶部 + 阅读进度条
- 移动端纯CSS汉堡菜单
- **武器对比表**: 斑马条纹表格，可排序(语义化`<thead>`)
- 地图标注: 图 + 侧边列表，点击列表项高亮对应标注(CSS `:target`)
- 战术: 步骤编号 + 信息框

### SEO
- Schema: Article + BreadcrumbList + Organization + WebSite
- Meta/OG/Twitter/Canonical 完整，武器页含武器名关键词

### 广告位
- 3个/页，纯自动广告，暗色底广告用浅色容器包裹

### 性能 + 无障碍
- 预连接 + lazy loading + 零JS + 语义化HTML + Skip to content

## 实现步骤

**执行前必读: `specs/MANDATORY_RULES.md`** — 所有强制规定必须在每个阶段逐条对照。

CF项目名: pubg-jycsd。

## 验收标准

```bash
ls pubg-site/weapons/*.html | wc -l                  # >= 6
ls pubg-site/maps/*.html | wc -l                     # >= 6
ls pubg-site/tactics/*.html | wc -l                  # >= 5
ls pubg-site/vehicles/*.html | wc -l                 # >= 4
ls pubg-site/updates/*.html | wc -l                  # >= 4
ls pubg-site/ranked/*.html | wc -l                   # >= 5
ls pubg-site/crates/*.html | wc -l                   # >= 5
ls pubg-site/roles/*.html | wc -l                    # >= 5
ls pubg-site/survival/*.html | wc -l                 # >= 5
ls pubg-site/settings/*.html | wc -l                 # >= 5
python shared/pre_commit_audit.py
python shared/check_portal_consistency.py
```

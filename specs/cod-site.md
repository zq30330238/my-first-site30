# cod-site — Call of Duty Guide (使命召唤)

---
MANDATORY_RULES_REF: specs/MANDATORY_RULES.md
STATUS: 本spec受MANDATORY_RULES.md约束，冲突时以总法为准。
---

## 基本信息

| 属性 | 值 |
|------|-----|
| 目录 | `cod-site/` |
| 域名 | cod.jycsd.com |
| 站点名称 | COD Arsenal |
| 品牌色 | `#22C55E` (军绿) + `#0A0A0A` (黑底) |
| 类型 | 暗色底 game 模板 |
| 受众 | 男性/18-35 |
| 月搜索量 | 2000万+ |
| 模板类型 | game 标准模板 (暗色) |
| 品牌 | Myers Media / Jordan Myers |

## 页面结构

```
cod-site/
├── index.html / about.html / contact.html / privacy-policy.html
├── terms.html / cookie-policy.html / sitemap.xml
├── robots.txt / ads.txt / favicon.ico
├── images/
│   ├── default-og.jpg / logo.svg
│   ├── games/              # 各代COD封面
│   ├── weapons/            # 武器图
│   └── banners/
├── games/                  # 各代COD (8页)
├── games/index.html        # 各代COD索引
├── weapons/                # 武器库 (5页)
├── weapons/index.html      # 武器库索引
├── maps/                   # 地图 (5页)
├── maps/index.html         # 地图库索引
├── multiplayer/            # 多人技巧 (4页)
├── multiplayer/index.html  # 多人技巧索引
├── campaign/               # 战役攻略 (4页)
├── campaign/index.html     # 战役攻略索引
├── zombies/                # 僵尸模式 (5页)
├── zombies/index.html      # 僵尸模式索引
├── warzone/                # 战区攻略 (5页)
├── warzone/index.html      # 战区攻略索引
├── operators/              # 特战兵 (5页)
├── operators/index.html    # 特战兵索引
├── esports/                # 电竞竞技 (5页)
├── esports/index.html      # 电竞竞技索引
├── settings/               # 设置优化 (5页)
├── settings/index.html     # 设置优化索引
└── index.html
```

总计约 **65页**。

> 参照站: naruto-site (游戏站模板)。每个分类子目录必须有 index.html 作为该分类的全部条目列表页。首页 'View All' 按钮链接到对应 guides/*/index.html。

## 分类设计

### 1. Games (各代COD, 8页)
- MW系列(4页): MW2019/MWII/MWIII/Black Ops 6
- Black Ops系列(2页): BO Cold War/BO6
- Warzone(1页)
- Classic(1页): MW2(2009)/BO2经典回顾

### 2. Weapons (武器, 5页)
- AR/SMG/Sniper/Shotgun/LMG
- 每页: 武器列表+配件推荐+配装方案(loadout)

### 3. Maps (地图, 5页)
- 经典多人地图分析: 点位/路线/模式适配

### 4. Multiplayer Tips (多人, 4页)
- 瞄准训练/移动技巧/连杀奖励/团队配合

### 5. Campaign Guides (战役, 4页)
- 各代战役攻略+彩蛋收集+难度技巧

### 6. Zombies Mode (僵尸模式)
- Zombies Mode Complete Beginner Guide: Perks, Pack-a-Punch, Mystery Box, rounds system explained
- Best Zombies Maps Ranked: Kino der Toten, Origins, Der Eisendrache, Shadows of Evil, Mob of the Dead analysis
- Zombies Easter Egg Guides: Main quest walkthroughs for top 5 maps
- Wonder Weapons Guide: Ray Gun, Wunderwaffe, Staffs, Bows, and how to obtain each
- Zombies Loadout & Strategy: Best starting weapons, Gobblegums, field upgrades, high-round strategies

### 7. Warzone Strategies (战区攻略)
- Warzone Complete Beginner Guide: Gulag, loadout drops, buy stations, contracts explained
- Best Warzone Landing Spots: Map-by-map drop spot analysis for safe and aggressive starts
- Warzone Loadout Meta: Current meta weapons, perk packages, equipment recommendations
- Warzone Movement Guide: Slide canceling, dropshotting, bunny hopping, mantle techniques
- Resurgence vs Battle Royale: Mode differences, respawn mechanics, strategy adjustments

### 8. Operators & Characters (特战兵)
- All COD Operators Guide: Complete operator roster, how to unlock each, faction overview
- Best Operator Skins: Most popular skins, crossover operators, limited edition cosmetics
- Operator Background Stories: Lore and backstories for iconic operators (Ghost, Price, Woods, Mason)
- Operator Faction Guide: SpecGru vs KorTac, faction-specific finishing moves and highlights
- How to Unlock Operators: Challenges, bundles, battle pass unlock conditions

### 9. Esports & Competitive (电竞与竞技)
- Call of Duty League (CDL) Overview: Teams, format, seasons, how to watch
- CDL Ruleset Explained: Maps, modes, banned items, competitive settings
- Pro Player Settings & Loadouts: Controller settings, sensitivity, FOV, pro loadout breakdowns
- Ranked Play Guide: SR system, skill divisions, rank rewards, solo queue tips
- Competitive Map Callouts: CDL map callout guides for every competitive map

### 10. Settings & Optimization (设置优化)
- Best Controller Settings: Sensitivity, deadzone, aim response curve, button layouts
- Best PC Settings for COD: Graphics, FOV, keybinds, audio settings for competitive play
- Aim Training Guide: Aim assist mechanics, recoil control drills, tracking exercises
- Audio Settings Deep Dive: Sound EQ, footsteps optimization, spatial audio comparison
- Performance Optimization: FPS boost settings, input lag reduction, network optimization

## 图片清单

| 类型 | 数量 | 来源 |
|------|------|------|
| 游戏封面 | 8 | 官方素材 |
| 武器图 | ~25 | 官方wiki/截图 |
| 地图鸟瞰 | 5 | 游戏截图 |
| Banner | 6 | 官方壁纸 |

## 首页区块

1. **Hero**: 军绿暗底 + 轮播≥5张
2. **Game Series**: 各代COD时间线
3. **Weapon Arsenal**: 武器库快速导航
4. **Latest**: 最新COD资讯
5. **Zombies Mode**: Perks, maps, Easter eggs navigation
6. **Warzone**: Battle royale & Resurgence guides
7. **Operators**: Character roster & skins showcase
8. **Esports**: CDL, ranked play, pro settings
9. **Settings & Optimization**: Controller, graphics, audio guides
10. **AdSense**: 3个广告位

## CTR与流量增长策略

### 标题优化
- 武器页: "MCW Loadout Guide - Best Attachments & Class Setup (BO6)"
- 地图页: "Nuketown Map Guide - Callouts, Spawn Points & Best Angles"
- 含游戏版本(BO6/MWIII/Warzone)精准定位玩家

### Meta Description
- 配装方案作为卖点
- 例: "Dominate with the MCW in Black Ops 6. Complete loadout guide with best attachments, perks, equipment, and alternative setups for every playstyle."

### Featured Snippet
- Loadout配装表进table snippet
- "Best MCW class setup?" → 列表(5配件+3perk)
- 地图callout用结构化列表

### 内链策略
- 武器页 → 推荐地图 + 同类武器对比
- 地图页 → 推荐武器
- 各代COD页 → 武器/地图/战役
- 更新新闻 → 受影响武器

### 内容新鲜度
- 武器meta随赛季更新
- 标注 "BO6 Season 3 Meta"
- 新地图/武器上线24小时内更新

### 回访机制
- "Compare Weapons" → 并排对比引导
- "More BO6 Loadouts" → 同代武器推荐
- COD时间线 → 代际浏览

### 富文本摘要
- Article Schema
- BreadcrumbList Schema

## 质量与UX标准

### 内容质量
- 武器页: 每武器 ≥150字 + 伤害/射速/后坐力数据 + Loadout配装
- 地图页: 标注点 ≥8处 + 模式适配建议
- 战役攻略: ≥800字，含关卡步骤
- 数据准确(从官方patch notes验证)
- 禁止AI cliché

### 视觉质量 — 军式暗色风格
- 军绿`#22C55E` + 黑底`#0A0A0A`，军式硬朗风
- 武器图: 渲染图+游戏内截图，`object-cover`
- 暗色底对比度重点验证: 绿字在纯黑底上需足够亮
- **禁止图片阴影遮罩**

### UX设计
- Banner轮播≥5张(纯CSS)
- COD时间线: 横排卡片，从左到右按发布时间排列
- 面包屑 + 返回顶部 + 阅读进度条
- 移动端纯CSS汉堡菜单
- **Loadout配装卡**: 代码块风格，武器+配件5槽+perk
- 武器对比: 并排双卡片

### SEO
- Schema: Article + BreadcrumbList + Organization + WebSite
- Meta/OG/Twitter/Canonical 完整

### 广告位
- 3个/页，纯自动广告，暗色底用浅色容器

### 性能 + 无障碍
- 预连接 + lazy loading + 零JS + 语义化HTML + Skip to content

## 实现步骤

**执行前必读: `specs/MANDATORY_RULES.md`** — 所有强制规定必须在每个阶段逐条对照。

CF项目名: cod-jycsd。

## 验收标准

```bash
ls cod-site/games/*.html | wc -l                     # >= 8
ls cod-site/weapons/*.html | wc -l                   # >= 5
ls cod-site/maps/*.html | wc -l                      # >= 5
ls cod-site/multiplayer/*.html | wc -l               # >= 4
ls cod-site/campaign/*.html | wc -l                  # >= 4
ls cod-site/zombies/*.html | wc -l                   # >= 5
ls cod-site/warzone/*.html | wc -l                   # >= 5
ls cod-site/operators/*.html | wc -l                 # >= 5
ls cod-site/esports/*.html | wc -l                   # >= 5
ls cod-site/settings/*.html | wc -l                  # >= 5
python shared/pre_commit_audit.py
python shared/check_portal_consistency.py
```

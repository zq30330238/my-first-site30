# roblox-site — Roblox Guide (Roblox攻略)

---
MANDATORY_RULES_REF: specs/MANDATORY_RULES.md
STATUS: 本spec受MANDATORY_RULES.md约束，冲突时以总法为准。
---

## 基本信息

| 属性 | 值 |
|------|-----|
| 目录 | `roblox-site/` |
| 域名 | roblox.jycsd.com |
| 站点名称 | Roblox Hub |
| 品牌色 | `#EF4444` (红) + `#FFFFFF` (白底), 多彩配色 |
| 类型 | 明亮底 game 模板 |
| 受众 | 儿童/青少年 + 家长 |
| 月搜索量 | 3000万+ |
| 模板类型 | game 标准模板 |
| 品牌 | Myers Media / Jordan Myers |

## 页面结构

```
roblox-site/
├── index.html / about.html / contact.html / privacy-policy.html
├── terms.html / cookie-policy.html / sitemap.xml
├── robots.txt / ads.txt / favicon.ico
├── images/
│   ├── default-og.jpg / logo.svg
│   ├── games/              # TOP20游戏截图
│   └── banners/
├── games/                  # TOP20热门游戏页
├── games/index.html        # 热门游戏索引 (20个)
├── scripting/              # 脚本教程 (5页)
├── scripting/index.html    # 脚本教程索引
├── avatar/                 # 装扮指南 (3页)
├── avatar/index.html       # 装扮指南索引
├── robux/                  # Robux货币指南 (3页)
├── robux/index.html        # 货币指南索引
├── parents/                # 家长指南 (3页)
├── parents/index.html      # 家长指南索引
├── trading/                # 交易与经济 (5页)
├── trading/index.html      # 交易与经济索引
├── gamedev/                # 游戏开发入门 (5页)
├── gamedev/index.html      # 开发指南索引
├── events/                 # 活动与季节内容 (5页)
├── events/index.html       # 活动指南索引
├── mobile/                 # 移动端与跨平台 (5页)
├── mobile/index.html       # 移动平台索引
├── community/              # 社区与社交 (5页)
├── community/index.html    # 社区指南索引
└── index.html
```

总计约 **65页**。

> 参照站: naruto-site (游戏站模板)。每个分类子目录必须有 index.html 作为该分类的全部条目列表页。首页 'View All' 按钮链接到对应 guides/*/index.html。

## 分类设计

### 1. Best Games (热门游戏 TOP20)
- 20个游戏独立页，每页: 游戏截图+玩法简介+人气数据+技巧
- 精选: Adopt Me, Brookhaven, Blox Fruits, Tower of Hell, MeepCity, Pet Simulator X, Murder Mystery 2, Arsenal, Jailbreak, Piggy, Doors, Rainbow Friends, BedWars, Blade Ball, Dress to Impress, Natural Disaster Survival, Phantom Forces, Theme Park Tycoon 2, Bee Swarm Simulator, Fisch

### 2. Scripting (脚本教程, 5页)
- Lua基础 / 脚本结构 / 事件处理 / 简单游戏制作 / 常见错误修复

### 3. Avatar & Items (装扮, 3页)
- 装扮基础 / 限定物品收集 / UGC创作入门

### 4. Robux Guide (货币指南, 3页)
- Robux获取方式 / 消费建议 / 安全防骗

### 5. Parents Guide (家长指南, 3页)
- 家长控制设置 / 消费管理 / 安全沟通

### 6. Trading & Economy (交易与经济)
- Roblox Trading System Explained: Trade requests, RAP value, value trends, Limited items
- Best Limited Items to Invest In: Market analysis, value history, safe investment strategies
- How to Avoid Trading Scams: Common scams, how to verify legit trades, trust signals
- Roblox Premium Benefits: Stipend, trading access, premium-only features
- Understanding RAP & Value: Recent Average Price, projected values, market manipulation awareness

### 7. Game Development Basics (游戏开发入门)
- Roblox Studio Complete Beginner Guide: Interface, toolbox, parts, materials, first build
- Lua Scripting for Beginners: Variables, functions, events, loops, practical examples
- How to Make a Simulator Game: Leaderstats, rebirth system, click detection, data stores
- Game Monetization Guide: Gamepasses, developer products, VIP servers, engagement-based payouts
- Publishing & Marketing Your Game: Sponsoring, thumbnail design, social media promotion

### 8. Events & Seasonal Content (活动与季节内容)
- Roblox Annual Events Guide: Egg Hunt, The Hunt, RB Battles, Innovation Awards
- Seasonal Event Items: Halloween, Christmas, Lunar New Year limited items
- How to Get Event Badges: Tracking events, exclusive rewards, limited-time challenges
- Roblox Creator Events: Developer conferences, RDC, creator challenges
- Upcoming Roblox Events: Event calendar, speculation, preparation tips

### 9. Mobile & Cross-Platform (移动端与跨平台)
- Roblox Mobile Guide: Controls, settings, optimization for phone/tablet
- Cross-Platform Play Differences: Mobile vs PC vs Console experience comparison
- Best Mobile-Friendly Roblox Games: Games optimized for touch controls
- Roblox on Console: Xbox/PlayStation features, limitations, controller setup
- VR Roblox Experience: VR-compatible games, setup guide, motion sickness tips

### 10. Community & Social Features (社区与社交)
- Roblox Groups Guide: Creating, managing, ranking, group funds explained
- How to Make Friends on Roblox: Friend requests, privacy settings, party system
- Roblox Chat & Communication: Safe chat, voice chat eligibility, filtering system
- Roblox Content Creators: Top YouTubers, streamers, and how to start your own channel
- Roblox Culture & Memes: Oof sound, Bacon Hair, Slenders, CNPs, and community terminology

## 图片清单

| 类型 | 数量 | 来源 |
|------|------|------|
| 游戏截图 | 40 (20游戏×2) | Roblox官方截图+YouTube视频截图 |
| Banner | 6 | 热门游戏截图 |

## 首页区块

1. **Hero**: 多彩渐变 + 热门游戏轮播 (6张)
2. **Top Games Grid**: 热门游戏卡片网格
3. **For Beginners**: 入门引导
4. **Parents Corner**: 家长信息区块
5. **Trading Hub**: 交易市场动态与限定物品策略
6. **Game Dev**: 开发入门与工作室指南
7. **Event Calendar**: 近期活动与季节内容
8. **Cross-Platform Tips**: 移动端/主机/VR使用技巧
9. **Community Spotlight**: 社区文化、创作者与社交指南
10. **AdSense**: 3个广告位

## CTR与流量增长策略

### 标题优化
- 游戏页: "Adopt Me! Guide 2026 - Best Tips, Tricks & Trading Values"
- 脚本教程: "How to Make Your First Roblox Game - Lua Scripting Tutorial"
- 家长指南: "Roblox Parental Controls: Complete Setup Guide (2026)"

### Meta Description
- 告诉用户页面的具体价值
- 例: "New to Adopt Me? Learn the best money-making methods, pet values, and trading tips. Complete guide updated for 2026."

### Featured Snippet
- 脚本代码块进code snippet
- "How to get free Robux?" → 回答+警告(防骗)
- 游戏列表用有序列表
- 家长设置步骤用HowTo

### 内链策略
- 游戏页 → 相关脚本教程
- 脚本教程 → 其他脚本页(进阶)
- Robux指南 → 家长指南(消费管理)
- 游戏推荐聚类: 同类游戏互链

### 内容新鲜度
- 游戏人气数据标注 "As of [Month Year]"
- 脚本教程标注适用Roblox版本
- 新热门游戏及时添加

### 回访机制
- "Discover More Games" → 游戏推荐引导
- 脚本学习路径: "Lua Basics → Your First Script → Building a Game"

### 富文本摘要
- Article Schema + HowTo Schema(教程) + TechArticle(脚本)
- BreadcrumbList Schema
- 游戏列表: ItemList Schema

## 质量与UX标准

### 内容质量
- 每个游戏页 ≥500字实质性内容(玩法+技巧+人气数据)
- 教程类页面(脚本/货币/装扮) ≥800字，含代码示例和步骤
- 所有内容适合青少年阅读，语言通俗
- 家长指南页面: 语言正式，提供可操作的安全设置步骤
- 禁止AI cliché

### 视觉质量
- 明亮多彩: 红色`#EF4444` + 白底 + 多彩游戏截图
- 游戏截图 `object-cover`，卡片横向布局
- 图片lazy loading + alt文本
- **禁止图片阴影遮罩**
- 脚本代码块: 深色背景`bg-gray-900` + 语法高亮色

### UX设计
- Banner轮播≥5张(纯CSS)
- TOP20游戏网格 + View All
- 面包屑 + 返回顶部 + 阅读进度条
- 移动端纯CSS汉堡菜单
- **脚本代码**: `<pre><code>` 带复制按钮(纯CSS，无JS)
- 家长指南: 步骤式checklist
- 游戏评分: 星级(CSS) + 适合年龄段标签

### SEO
- Schema: Article + BreadcrumbList + Organization + WebSite + (脚本页加TechArticle)
- Meta/OG/Twitter/Canonical 完整

### 广告位
- 3个/页，纯自动广告，禁止手动广告位
- **注意**: 受众含青少年，广告不涉及敏感类别

### 性能 + 无障碍
- 预连接 + lazy loading + 零JS + 语义化HTML + Skip to content

## 实现步骤

**执行前必读: `specs/MANDATORY_RULES.md`** — 所有强制规定必须在每个阶段逐条对照。

CF项目名: roblox-jycsd。

## 验收标准

```bash
ls roblox-site/games/*.html | wc -l                 # >= 20
ls roblox-site/scripting/*.html | wc -l             # >= 5
ls roblox-site/avatar/*.html | wc -l                # >= 3
ls roblox-site/robux/*.html | wc -l                 # >= 3
ls roblox-site/parents/*.html | wc -l               # >= 3
ls roblox-site/trading/*.html | wc -l               # >= 5
ls roblox-site/gamedev/*.html | wc -l               # >= 5
ls roblox-site/events/*.html | wc -l                # >= 5
ls roblox-site/mobile/*.html | wc -l                # >= 5
ls roblox-site/community/*.html | wc -l             # >= 5
python shared/pre_commit_audit.py
python shared/check_portal_consistency.py
```

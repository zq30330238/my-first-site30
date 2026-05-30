# sololeveling-site — Solo Leveling Wiki (我独自升级)

---
MANDATORY_RULES_REF: specs/MANDATORY_RULES.md
STATUS: 本spec受MANDATORY_RULES.md约束，冲突时以总法为准。
---

## 基本信息

| 属性 | 值 |
|------|-----|
| 目录 | `sololeveling-site/` |
| 域名 | sololeveling.jycsd.com |
| 站点名称 | Solo Leveling Archive |
| 品牌色 | `#8B5CF6` (紫) + `#0F172A` (深蓝底) |
| 类型 | 暗色底 anime 模板 (韩风) |
| 受众 | 全球动漫/网漫迷 |
| 月搜索量 | 500万+ |
| 模板类型 | anime 标准模板 (暗色) |
| 品牌 | Myers Media / Jordan Myers |

## 页面结构

```
sololeveling-site/
├── index.html / about.html / contact.html / privacy-policy.html
├── terms.html / cookie-policy.html / sitemap.xml
├── robots.txt / ads.txt / favicon.ico
├── images/
│   ├── default-og.jpg / logo.svg
│   ├── characters/         # 角色图 (~36张)
│   ├── shadows/            # 影军
│   └── banners/
├── characters/             # 12个角色页
├── characters/index.html   # 角色索引 (12个)
├── dungeons/               # 地下城 (5页)
├── dungeons/index.html     # 地下城索引
├── arcs/                   # 8个篇章
├── arcs/index.html         # 篇章索引 (8个)
├── ranks/                  # 等级系统 (3页)
├── ranks/index.html        # 等级系统索引
├── shadow-army/            # 影之军队 (4页)
├── shadow-army/index.html  # 影之军队索引
├── skills/                 # 技能与能力 (5页)
├── skills/index.html       # 技能索引
├── items/                  # 物品与装备 (5页)
├── items/index.html        # 物品索引
├── guilds/                 # 公会与组织 (5页)
├── guilds/index.html       # 公会索引
├── monarchs/               # 君主与统治者 (5页)
├── monarchs/index.html     # 君主索引
├── system/                 # 系统与任务 (5页)
├── system/index.html       # 系统索引
└── index.html
```

总计约 **70页**。

> 参照站: aot-site (动漫站模板)。每个分类子目录必须有 index.html 作为该分类的全部条目列表页。首页 'View All' 按钮链接到对应 guides/*/index.html。

## 分类设计

### 1. Characters (角色, 12个)
- Sung Jin-Woo / Cha Hae-In / Yoo Jin-Ho / Go Gun-Hee / Baek Yoon-Ho / Choi Jong-In / Thomas Andre / Liu Zhigang / Christopher Reed / Lee Joo-Hee / Woo Jin-Chul / Hwang Dong-Soo
- 每页: 角色大图+等级+能力+剧情线

### 2. Dungeons (地下城, 5页)
- E-Rank to S-Rank Gates / Red Gate / Jeju Island Raid / Double Dungeon / Monarch Gates
- 每页: 地下城等级+怪物+Boss+攻略

### 3. Arcs (篇章, 8个)
- D-Rank Dungeon Arc / Reawakening Arc / Demon Castle Arc / Retesting Rank Arc / Jeju Island Arc / International Guild Conference Arc / Monarch War Arc / Final Battle

### 4. Ranks (等级系统, 3页)
- Hunter Ranking (E→S→National Level) / Jin-Woo's Level Progression / Monarch & Rulers

### 5. Shadow Army (影之军队, 4页)
- Shadow Extraction / Igris / Beru / Bellion & Grand Marshal
- 每页: 影军角色图+等级+战斗能力

### 6. Skills & Abilities (技能与能力)
- Jin-Woo's Complete Skill Tree: Stealth, Bloodlust, Ruler's Authority, Quicksilver, Dagger Rush, Mutilation, and all acquired skills
- Shadow Monarch Exclusive Abilities: Shadow Extraction, Shadow Exchange, Shadow Preservation, Domain of the Monarch
- Hunter Class Abilities: Fighter/Mage/Assassin/Tanker/Healer/Ranger class skills and awakening types
- Monarch & Ruler Abilities: Power comparison, divine abilities, dimensional manipulation
- System Skills & Interface: System shop, daily quest rewards, stat allocation, skill runes explained

### 7. Items & Equipment (物品与装备)
- Jin-Woo's Equipment Catalog: Kasaka's Venom Fang, Demon King's Daggers, Kamish's Wrath, full equipment list
- System Shop Items: Healing potions, stat-enhancing items, consumables, box items
- Legendary & Mythic Grade Items: Holy Water of Life, Elixir of Life, Cup of Reincarnation
- Hunter Gear & Artifacts: Gate-extracted magical items, weapon tiers, armor categories
- Crafting & Enhancement: Item crafting in Solo Leveling, enhancement systems, material acquisition

### 8. Guilds & Organizations (公会与组织)
- Top Korean Guilds: Hunters Guild, Fame Guild, Knights Guild, Ahjin Guild — leaders, strength, politics
- International Guilds: Scavenger Guild (USA), Asura Guild (India), China's top guilds
- Hunter's Association: Go Gun-Hee's leadership, association structure, rank certification
- Guild Politics & Economics: Gate rights, dungeon profit distribution, inter-guild rivalries
- Ahjin Guild Deep Dive: Jin-Woo's personal guild, founding, growth, Yoo Jin-Ho's role

### 9. Monarchs & Rulers (君主与统治者)
- The Nine Monarchs Guide: Shadow, Beast, Frost, Plague, Iron Body, Giant, Dragon, Demon, Insect Monarchs full profiles
- The Rulers (Angels): Seven Rulers identities, purpose, conflict with Monarchs, hidden agenda
- Monarch War Arc: Complete breakdown of the Monarch-Ruler conflict and earth invasion
- Ashborn — Greatest Brilliant Light: His betrayal, succession, relation to Jin-Woo
- Divine Beings & Creation Myth: Absolute Being, the original war, creating the system

### 10. System & Quests (系统与任务)
- The System Complete Guide: Origin (Ashborn's creation), purpose, leveling mechanics, hidden features
- Daily Quest Breakdown: Push-ups, sit-ups, running, demon castle alternatives, penalty zone
- Main Story Quests: Key quests that drove Jin-Woo's progression, hidden quest conditions
- Emergency & Hidden Quests: Trigger conditions, rewards, difficulty comparison
- The System's Evolution: System awakening to full Shadow Monarch power, system removal

## 图片清单

| 类型 | 数量 | 来源 |
|------|------|------|
| 角色图 | 36 | pngwing.com + 网漫截图 |
| 影军图 | 12 | 网漫截图 |
| Banner | 6 | 官方壁纸 |

## 首页区块

1. **Hero**: 紫色暗底 + 轮播≥5张 (Sung Jin-Woo各形态)
2. **Featured Characters**: 角色轮播
3. **Shadow Army**: 影军展示
4. **Dungeon Guide**: 地下城导航
5. **Skills & Abilities**: 技能树展示
6. **Items & Equipment**: 传说装备展示
7. **Guilds & Organizations**: 公会名录
8. **Monarchs & Rulers**: 君王档案
9. **System & Quests**: 系统机制解析
10. **AdSense**: 3个广告位

## CTR与流量增长策略

### 标题优化
- 角色页: "Sung Jin-Woo - Shadow Monarch: Full Powers, Abilities & Level Progression"
- 影军页: "Igris - The Blood-Red Commander: Abilities, Battles & Loyalty"
- 突出等级/影军/地下城等核心系统

### Meta Description
- 角色成长弧+核心设定
- 例: "Follow Sung Jin-Woo's journey from E-Rank hunter to Shadow Monarch. Complete guide to his abilities, shadow army, level progression, and every major battle."

### Featured Snippet
- 等级系统表(Hunter Rank E→S→National)
- "How strong is Sung Jin-Woo?" → 等级/能力列表
- 地下城难度对比表

### 内链策略
- 角色↔影军成员(主从关系)
- 地下城↔登场的角色+影军
- 篇章↔登场角色
- 等级系统↔各等级代表角色

### 内容新鲜度
- 动画S2/剧场版同步更新
- Ragnarok续作内容单独标注

### 回访机制
- "Explore Shadow Army" → 影军指挥体系浏览
- 等级成长时间线导航
- 篇章连续阅读

### 富文本摘要
- Article Schema + ItemList Schema + BreadcrumbList Schema

## 质量与UX标准

### 内容质量
- 角色页 ≥500字(等级+能力+剧情线)
- 地下城页 ≥400字(Boss+攻略+掉落)
- 篇章页 ≥600字
- 数据准确(原作设定)
- 禁止AI cliché

### 视觉质量 — 韩风暗色
- 紫色`#8B5CF6` + 深蓝底`#0F172A`，韩式暗色风格
- 大图角色卡，`object-cover`
- 暗色对比度: 正文`#CBD5E1` + 标题`#A78BFA`通过WCAG AA
- **禁止图片阴影遮罩**
- 等级badge: E/D/C/B/A/S/National Level 渐变色标签
- 影军: 紫色调暗色卡片

### UX设计
- 角色轮播 + 影军展示 + Banner轮播≥5张(纯CSS)
- 面包屑 + 返回顶部 + 阅读进度条
- 移动端纯CSS汉堡菜单
- **等级进度**: 竖向timeline，节点用CSS圆形+等级字母
- 影军指挥体系: 树形结构(CSS indentation)
- 地下城难度: 星级+等级标签

### SEO
- Schema: Article + BreadcrumbList + Organization + WebSite
- Meta/OG/Twitter/Canonical 完整

### 广告位
- 3个首页/2个详情页，纯自动广告，暗色容器包裹

### 性能 + 无障碍
- 预连接 + lazy loading + 零JS + 语义化HTML + Skip to content

## 实现步骤

**执行前必读: `specs/MANDATORY_RULES.md`** — 所有强制规定必须在每个阶段逐条对照。

CF项目名: sololeveling-jycsd。

## 验收标准

```bash
ls sololeveling-site/characters/*.html | wc -l          # >= 12
ls sololeveling-site/dungeons/*.html | wc -l            # >= 5
ls sololeveling-site/arcs/*.html | wc -l                # >= 8
ls sololeveling-site/shadow-army/*.html | wc -l         # >= 4
ls sololeveling-site/skills/*.html | wc -l              # >= 5
ls sololeveling-site/items/*.html | wc -l               # >= 5
ls sololeveling-site/guilds/*.html | wc -l              # >= 5
ls sololeveling-site/monarchs/*.html | wc -l            # >= 5
ls sololeveling-site/system/*.html | wc -l              # >= 5
python shared/pre_commit_audit.py
python shared/check_portal_consistency.py
```

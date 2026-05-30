# sub-outdoor — Outdoor & Camping (户外/露营/徒步)

---
MANDATORY_RULES_REF: specs/MANDATORY_RULES.md
STATUS: 本spec受MANDATORY_RULES.md约束，冲突时以总法为准。
---

## 基本信息

| 属性 | 值 |
|------|-----|
| 目录 | `sub-outdoor/` |
| 域名 | outdoor.jycsd.com |
| 站点名称 | Trail & Summit |
| 品牌色 | `#059669` (翠绿) + `#ECFDF5` (浅绿底) |
| 受众 | 20-50岁户外爱好者 |
| 赛道CPC | $1-3 |
| 竞争度 | 低 (蓝海) |
| 模板类型 | content 标准模板 |
| 品牌 | Myers Media / Jordan Myers |

## 页面结构

```
sub-outdoor/
├── index.html / about.html / contact.html / privacy-policy.html
├── terms.html / cookie-policy.html / sitemap.xml
├── robots.txt / ads.txt / favicon.ico
├── images/
│   ├── default-og.jpg / logo.svg
│   └── article-*.jpg (30张)
├── articles.html               # 全部文章列表页
├── category-camping.html       # 分类1文章列表 (6篇)
├── category-hiking.html        # 分类2文章列表 (6篇)
├── category-fishing.html       # 分类3文章列表 (6篇)
├── category-gear-reviews.html  # 分类4文章列表 (6篇)
└── category-survival-skills.html # 分类5文章列表 (6篇)
```

参照站: sub-healthy (内容站模板)。页面结构必须与参照站一致。分类卡片链接到 category-*.html，View All 链接到 articles.html。

## 分类设计

### 1. Camping (露营)
- **覆盖**: Tent selection, campsite setup, camping with kids, camp cooking, seasonal camping, car camping vs backpacking

### 2. Hiking (徒步)
- **覆盖**: Trail guides, day hike preparation, multi-day trekking, navigation, elevation training, best hiking destinations

### 3. Fishing (钓鱼)
- **覆盖**: Freshwater basics, saltwater techniques, gear selection, fly fishing intro, seasonal patterns, catch and release

### 4. Gear Reviews (装备评测)
- **覆盖**: Backpack comparison, sleeping bag ratings, tent reviews, stove systems, footwear testing, budget gear guide

### 5. Survival Skills (生存技能)
- **覆盖**: Fire starting, water purification, shelter building, first aid outdoors, navigation without GPS, weather reading

## 扩展类别（新增12个）

### 6. Backpacking & Trekking (背包徒步)
- **标题**: Carry Your Life, Explore the Wild
- **覆盖**: Multi-day packing lists, lightweight gear, route planning, navigation skills, thru-hiking, altitude preparation

### 7. Rock Climbing (攀岩)
- **标题**: Reach New Heights
- **覆盖**: Bouldering vs sport vs trad, climbing grades, gear essentials, belay technique, indoor gym guide, climbing destinations

### 8. Water Sports (水上运动)
- **标题**: Paddle, Row, Explore
- **覆盖**: Kayaking basics, canoe technique, stand-up paddleboarding, rafting, water safety, best waterways by region

### 9. Winter Sports (冬季运动)
- **标题**: Embrace the Cold
- **覆盖**: Skiing vs snowboarding, cross-country skiing, snowshoeing, ice climbing, winter camping gear, avalanche safety

### 10. Mountain Biking (山地骑行)
- **标题**: Ride the Trails
- **覆盖**: Bike types explained, trail difficulty ratings, maintenance basics, protective gear, best MTB destinations, bikepacking

### 11. Trail Running (越野跑)
- **标题**: Run Beyond the Pavement
- **覆盖**: Trail vs road running, shoe selection, nutrition and hydration, elevation training, ultra running intro, navigation

### 12. Wildlife Photography (野生动物摄影)
- **标题**: Capture Nature's Moments
- **覆盖**: Camera gear for wildlife, field techniques, animal behavior basics, ethical photography, best locations, editing tips

### 13. National Parks Guide (国家公园指南)
- **标题**: America's Best Outdoor Spaces
- **覆盖**: Park-by-park guides, best hiking trails, camping reservations, seasonal timing, hidden gems, park regulations

### 14. Outdoor Cooking (户外烹饪)
- **标题**: Eat Well in the Wild
- **覆盖**: Camp stove comparison, Dutch oven recipes, dehydrated meals, foraging basics, campfire cooking, bear-safe food storage

### 15. First Aid & Safety (急救与安全)
- **标题**: Stay Safe Outdoors
- **覆盖**: Wilderness first aid, emergency signaling, weather reading, wildlife encounters, navigation emergency, survival priorities

### 16. Stargazing & Astronomy (观星)
- **标题**: Explore the Night Sky
- **覆盖**: Telescope guide, constellation identification, astrophotography basics, dark sky parks, meteor shower calendar, moon phases

### 17. Bushcraft & Wilderness Skills (野外生存)
- **标题**: Master the Wild
- **覆盖**: Fire starting methods, shelter building, water purification, knife skills, cordage and knots, edible plant identification

## 图片清单

| 类型 | 数量 | 来源 |
|------|------|------|
| 文章封面 | 30 | Unsplash (outdoor/camping/hiking) |
| OG默认图 | 1 | 品牌色底+logo |

**Unsplash搜索关键词**: camping tent, hiking trail mountain, outdoor adventure, forest landscape, fishing lake, backpacking gear, campfire, national park, survival shelter, starry sky camping

**注**: 户外类图片Unsplash资源极其丰富，下载难度最低。

## 首页区块

1. **Hero**: 大图背景(户外风景) + "Explore the Outdoors with Confidence"
2. **Featured Categories**: 5分类卡片
3. **Latest Articles**: 6篇
4. **Gear Picks**: 精选装备推荐区
5. **AdSense**: 3个广告位

## 文章结构 (1000-1500字/篇)

三段式。装备评测类文章需含对比表。每分类6篇。

## CTR与流量增长策略

### 标题优化
- "The Complete Camping Checklist: 50+ Items You Shouldn't Forget"
- "10 Best Hiking Trails in [Region] for Beginners (2026 Guide)"
- 数字+地点+年份组合
- 长度≤60字符

### Meta Description
- 地理定位关键词 + CTA
- 例: "Planning your first camping trip? Download our complete checklist with 50+ essential items. Plus tent selection tips and campsite setup guide for beginners."

### Featured Snippet
- Checklist进列表snippet
- "What to bring camping?" → 40-60字回答 + 列表
- 装备对比表进table snippet
- 地点推荐用有序列表

### 内链策略
- 露营↔徒步↔装备评测三角互链
- 地点文章链接装备文章: "For this trail, we recommend..."
- Related Articles + Read Next

### 内容新鲜度
- 季节性内容轮换(夏季露营/冬季生存技能)
- 装备评测标注评测年份
- 地点信息标注 "Conditions as of [date]"

### 回访机制
- Checklist可打印(用户带出去用=品牌持续曝光)
- 内容系列: "Camping 101 Series"

### 富文本摘要
- FAQ Schema
- HowTo Schema (搭帐篷/生火等步骤类)
- Review Schema (装备评测)
- BreadcrumbList Schema

## 质量与UX标准

### 内容质量
- 每篇文章 ≥1200字，装备评测类含对比表
- 文章结构: 导语钩子 → ToC → Key Takeaways → 正文3段 → FAQ → 结论
- 阅读时间标注 + 最后更新日期
- 禁止AI cliché
- 地点信息引用官方来源(NPS/AllTrails)，不编造路线数据

### 视觉质量
- 封面图16:9，lazy loading，alt文本描述场景
- 绿色`#059669`在浅绿底`#ECFDF5`上对比度通过WCAG AA
- 装备对比表: 斑马条纹，语义化`<table>`
- 禁止图片阴影遮罩(户外风景图尤其重要)

### UX设计
- 面包屑 + 文章ToC(桌面sticky) + 相关文章(3篇) + 返回顶部 + 阅读进度条
- 移动端纯CSS汉堡菜单
- 装备评分: 星级(CSS实现，无JS)，每个装备 评分/价格区间/适合人群
- 露营地/徒步路线: checklist格式(CSS checkbox模拟)，用户可打印

### SEO
- Schema: Article + BreadcrumbList + Organization + WebSite + FAQ + (装备评测加Review)
- Meta/OG/Twitter/Canonical 完整
- 内部链接每篇2-3个

### 广告位
- 3个/篇，纯自动广告，禁止手动广告位

### 性能 + 无障碍
- 预连接 + lazy loading + 零JS + 语义化HTML + Skip to content + 键盘可导航 + 打印友好

## 实现步骤

**执行前必读: `specs/MANDATORY_RULES.md`** — 所有强制规定必须在每个阶段逐条对照。

1-9步流程。CF项目名: outdoor-jycsd。

## 验收标准

```bash
ls sub-outdoor/article-*.html | wc -l                    # >= 102
ls sub-outdoor/category-*.html | wc -l                   # >= 17
grep -c 'article-card' sub-outdoor/index.html            # >= 6
python shared/pre_commit_audit.py
python shared/check_portal_consistency.py
python shared/health_check_daily.py --quality
python shared/refresh_sitemap.py sub-outdoor
```

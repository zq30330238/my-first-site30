# sub-fitness — Fitness & Training (健身/运动)

---
MANDATORY_RULES_REF: specs/MANDATORY_RULES.md
STATUS: 本spec受MANDATORY_RULES.md约束，冲突时以总法为准。
---

## 基本信息

| 属性 | 值 |
|------|-----|
| 目录 | `sub-fitness/` |
| 域名 | fitness.jycsd.com |
| 站点名称 | Fit Forge |
| 品牌色 | `#EF4444` (红) + `#111827` (深灰) |
| 受众 | 20-45岁健身爱好者 |
| 赛道CPC | $2-4 |
| 竞争度 | 高 |
| 模板类型 | content 标准模板 |
| 品牌 | Myers Media / Jordan Myers |

## 页面结构

```
sub-fitness/
├── index.html / about.html / contact.html / privacy-policy.html
├── terms.html / cookie-policy.html / sitemap.xml
├── robots.txt / ads.txt / favicon.ico
├── images/
│   ├── default-og.jpg / logo.svg
│   └── article-*.jpg (30张)
├── articles.html              # 全部文章列表页
├── category-strength.html     # 分类1文章列表 (6篇)
├── category-cardio.html       # 分类2文章列表 (6篇)
├── category-flexibility.html  # 分类3文章列表 (6篇)
├── category-nutrition.html    # 分类4文章列表 (6篇)
└── category-home-workouts.html # 分类5文章列表 (6篇)
```

参照站: sub-healthy (内容站模板)。页面结构必须与参照站一致。分类卡片链接到 category-*.html，View All 链接到 articles.html。

## 分类设计

### 1. Strength Training (力量训练)
- **覆盖**: Compound lifts, progressive overload, program design, form guides, rep ranges, strength standards

### 2. Cardio (有氧)
- **覆盖**: Running plans, HIIT protocols, cycling, swimming, heart rate zones, steady state vs intervals

### 3. Flexibility (柔韧)
- **覆盖**: Stretching routines, yoga for athletes, mobility drills, foam rolling, injury prevention, recovery

### 4. Nutrition for Athletes (运动营养)
- **覆盖**: Macro calculation, meal timing, supplements evidence, hydration, pre/post workout, cutting vs bulking

### 5. Home Workouts (家庭健身)
- **覆盖**: Bodyweight programs, minimal equipment, resistance bands, dumbbell-only, apartment-friendly, space setup

## 扩展类别（新增12个）

### 6. Yoga & Mobility (瑜伽与灵活性)
- **标题**: Flow & Flexibility
- **覆盖**: Yoga styles comparison, mobility drills, foam rolling, stretching science, yoga for athletes, restorative practice

### 7. HIIT & CrossFit (高强度间歇与CrossFit)
- **标题**: Maximum Results, Minimum Time
- **覆盖**: HIIT protocols, CrossFit WODs, Tabata, metabolic conditioning, AMRAP/EMOM formats, injury prevention

### 8. Running & Marathon (跑步与马拉松)
- **标题**: From Couch to Finish Line
- **覆盖**: 5K to marathon training plans, running form, shoe selection, injury prevention, trail running, race day nutrition

### 9. Weightlifting & Powerlifting (举重与力量举)
- **标题**: Lift Heavy, Build Strong
- **覆盖**: Compound lifts technique (squat/bench/deadlift), progressive overload, programming cycles, competition prep, accessory work

### 10. Bodyweight Training (自重训练)
- **标题**: Train Anywhere, No Equipment
- **覆盖**: Calisthenics progression, pull-up mastery, push-up variations, handstand training, park workout design, gymnastic rings

### 11. Recovery & Injury Prevention (恢复与伤病预防)
- **标题**: Train Smarter, Recover Faster
- **覆盖**: Active recovery, sleep optimization, ice bath vs sauna, common lifting injuries, prehab exercises, deload weeks

### 12. Sports Nutrition (运动营养)
- **标题**: Fuel for Performance
- **覆盖**: Macro timing, pre/post workout meals, supplements evidence review, hydration protocols, meal prep for athletes, competition fueling

### 13. Mental Fitness (心理素质)
- **标题**: The Mind-Muscle Connection
- **覆盖**: Motivation psychology, habit formation, goal setting, visualization, competition mindset, overcoming plateaus

### 14. Gym Equipment Guides (健身器材指南)
- **标题**: Build Your Home Gym
- **覆盖**: Equipment comparisons (barbell/dumbbell/kettlebell/cable), budget home gym setup, commercial gym navigation, wearable tech review

### 15. Fitness Tech & Apps (健身科技)
- **标题**: Tech-Powered Training
- **覆盖**: Best fitness apps, heart rate monitor guide, smartwatch for fitness, workout tracking, AI coaching, virtual training platforms

### 16. Swimming & Water Sports (游泳与水上运动)
- **标题**: Train in the Water
- **覆盖**: Swim stroke technique, pool workouts, open water swimming, triathlon swim training, aqua jogging, water safety

### 17. Senior Fitness (中老年健身)
- **标题**: Stay Active at Any Age
- **覆盖**: Low-impact exercises, balance training, bone density, joint-friendly workouts, flexibility for seniors, fall prevention

## 特殊设计

- **Workout Plan 表格**: 结构化训练计划 (day/exercise/sets/reps/rest)，用HTML table，Tailwind样式
- 文章内嵌表格示例:
```html
<table class="w-full text-left border-collapse">
  <thead><tr class="bg-gray-800 text-white">
    <th class="p-3">Day</th><th class="p-3">Exercise</th><th class="p-3">Sets</th><th class="p-3">Reps</th>
  </tr></thead>
  <tbody><!-- workout rows --></tbody>
</table>
```

## 图片清单

| 类型 | 数量 | 来源 |
|------|------|------|
| 文章封面 | 30 | Unsplash (gym/fitness/exercise) |
| OG默认图 | 1 | 品牌色底+logo |

**Unsplash搜索关键词**: gym workout, weight training, fitness exercise, running outdoor, yoga stretch, dumbbell, kettlebell, bodyweight exercise, athlete nutrition

## 首页区块

1. **Hero**: 深色底+红色accent + "Build Your Strongest Self"
2. **Featured Categories**: 5分类卡片
3. **Latest Articles**: 6篇
4. **Featured Workout Plan**: 精选训练计划预览卡片
5. **AdSense**: 3个广告位

## 文章结构 (1000-1500字/篇)

三段式 + 结构化训练表格。力量/有氧类文章必须含workout plan表格。每分类6篇。

## CTR与流量增长策略

### 标题优化
- "The 12-Week Strength Training Program That Actually Works"
- "7 HIIT Workouts You Can Do in 20 Minutes (No Equipment)"
- 含数字+强力词+具体承诺
- 长度≤60字符

### Meta Description
- 150-160字符，告诉用户点进来得到什么
- 例: "Build muscle and burn fat with our 12-week science-backed strength program. Includes workout tables, rep schemes, and nutrition tips. Start your transformation today."

### Featured Snippet
- Workout Plan表格直接进table snippet
- "How many reps for muscle growth?" → 40-60字直接回答
- 步骤类内容用有序列表

### 内链策略
- 训练文章链接营养文章(互补)
- 力量→有氧→柔韧 三角互链
- Related Articles + Read Next
- 孤岛页面零容忍

### 内容新鲜度
- Last updated日期
- 训练计划标注适用时间段(如 "2026 Summer Shred Plan")
- 首页每周轮换Featured Workout

### 回访机制
- 训练计划系列化: "Phase 1: Foundation → Phase 2: Build → Phase 3: Peak"
- 打印友好: 训练表格 + checklist可打印带去健身房

### 富文本摘要
- FAQ Schema: 每篇3-5个Q&A
- HowTo Schema: 训练步骤类文章
- 表格类内容: 标注 `itemtype="https://schema.org/Table"`

## 质量与UX标准

### 内容质量
- 每篇文章 ≥1200字，训练计划类文章含结构化workout table
- 文章结构: 导语钩子 → ToC → Key Takeaways → 正文3段 → Workout Plan表格 → FAQ → 结论
- 阅读时间标注 + 最后更新日期
- 禁止AI cliché
- 训练数据/研究引用必须有来源，不确定标注"general fitness advice"

### 视觉质量
- 封面图16:9，lazy loading，alt文本描述动作/器械
- 红色`#EF4444`在深灰`#111827`上对比度通过WCAG AA
- Workout Plan表格: 斑马条纹，移动端横向滚动，`<thead>`语义化表头
- 禁止图片阴影遮罩

### UX设计
- 面包屑 + 文章ToC(桌面sticky) + 相关文章(3篇) + 返回顶部 + 阅读进度条
- 移动端纯CSS汉堡菜单
- Workout Plan表格: 打印友好样式(`@media print`)
- 分类页: 可筛选按难度/时长/器材

### SEO
- Schema: Article + BreadcrumbList + Organization + WebSite + FAQ + (如含训练表加HowTo)
- Meta/OG/Twitter/Canonical 完整
- 内部链接每篇2-3个

### 广告位
- 3个/篇(导语后+正文中+结论前)，纯自动广告，禁止手动广告位

### 性能 + 无障碍
- 预连接 + lazy loading + 零JS + 语义化HTML + Skip to content + 键盘可导航

## 实现步骤

**执行前必读: `specs/MANDATORY_RULES.md`** — 所有强制规定必须在每个阶段逐条对照。

1-9步流程。CF项目名: fitness-jycsd。

## 验收标准

```bash
ls sub-fitness/article-*.html | wc -l                    # >= 102
ls sub-fitness/category-*.html | wc -l                   # >= 17
grep -c 'article-card' sub-fitness/index.html            # >= 6
grep -c '<table' sub-fitness/article-*.html | head -5     # 力量/有氧类文章含表格
python shared/pre_commit_audit.py
python shared/check_portal_consistency.py
python shared/health_check_daily.py --quality
python shared/refresh_sitemap.py sub-fitness
```

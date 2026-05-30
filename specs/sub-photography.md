# sub-photography — Photography Tutorials (摄影教程/器材)

---
MANDATORY_RULES_REF: specs/MANDATORY_RULES.md
STATUS: 本spec受MANDATORY_RULES.md约束，冲突时以总法为准。
---

## 基本信息

| 属性 | 值 |
|------|-----|
| 目录 | `sub-photography/` |
| 域名 | photography.jycsd.com |
| 站点名称 | Shutter Academy |
| 品牌色 | `#1E293B` (深灰蓝) + `#F1F5F9` (浅灰底) |
| 受众 | 18-50岁摄影爱好者 |
| 赛道CPC | $1-3 |
| 竞争度 | 低 |
| 模板类型 | content 标准模板 |
| 品牌 | Myers Media / Jordan Myers |

## 页面结构

```
sub-photography/
├── index.html / about.html / contact.html / privacy-policy.html
├── terms.html / cookie-policy.html / sitemap.xml
├── robots.txt / ads.txt / favicon.ico
├── images/
│   ├── default-og.jpg / logo.svg
│   └── article-*.jpg (30张)
├── articles.html                  # 全部文章列表页
├── category-camera-basics.html    # 分类1文章列表 (6篇)
├── category-composition.html      # 分类2文章列表 (6篇)
├── category-lighting.html         # 分类3文章列表 (6篇)
├── category-post-processing.html  # 分类4文章列表 (6篇)
└── category-gear-guides.html      # 分类5文章列表 (6篇)
```

参照站: sub-healthy (内容站模板)。页面结构必须与参照站一致。分类卡片链接到 category-*.html，View All 链接到 articles.html。

## 分类设计

### 1. Camera Basics (相机基础)
- **覆盖**: Exposure triangle, aperture/shutter/ISO, sensor sizes, lens types, manual mode, RAW vs JPEG

### 2. Composition (构图)
- **覆盖**: Rule of thirds, leading lines, framing, symmetry, negative space, golden ratio, perspective

### 3. Lighting (用光)
- **覆盖**: Natural light, golden hour, studio lighting, flash basics, reflectors, low light techniques, high key vs low key

### 4. Post-Processing (后期)
- **覆盖**: Lightroom workflow, color grading, retouching basics, presets, HDR merging, panorama stitching, export settings

### 5. Gear Guides (器材指南)
- **覆盖**: Camera body comparison, lens buying guide, tripod selection, filter types, bag recommendations, budget kit builds

## 扩展类别（新增12个）

### 6. Portrait Photography (人像摄影)
- **标题**: Capture the Human Spirit
- **覆盖**: Natural light portraits, studio lighting setups, posing guide, family portraits, headshots, candid photography

### 7. Landscape & Nature (风光与自然)
- **标题**: Chase the Light
- **覆盖**: Golden hour mastery, long exposure, panorama technique, weather planning, location scouting, filters guide

### 8. Street Photography (街头摄影)
- **标题**: Find Art in Everyday Life
- **覆盖**: Zone focusing, discreet shooting, decisive moment, legal and ethics, storytelling, black and white street

### 9. Wedding & Event (婚礼与活动)
- **标题**: Document Life's Biggest Moments
- **覆盖**: Shot lists, dual camera setup, lighting challenges, client communication, contract basics, album design

### 10. Product & Commercial (产品与商业摄影)
- **标题**: Shoot Products That Sell
- **覆盖**: Lightbox technique, product styling, flat lay, e-commerce specs, reflection control, client briefs

### 11. Mobile Photography (手机摄影)
- **标题**: Pro Photos from Your Pocket
- **覆盖**: Best camera apps, phone lens accessories, mobile editing, social media optimization, print from phone, computational photography

### 12. Drone Photography (无人机摄影)
- **标题**: See the World from Above
- **覆盖**: Drone selection, FAA regulations, aerial composition, video basics, panoramic from above, safety checklist

### 13. Night & Low-Light (夜景与弱光)
- **标题**: Paint with Light
- **覆盖**: Tripod technique, long exposure, astrophotography, city lights, light painting, high ISO management

### 14. Black & White (黑白摄影)
- **标题**: The Power of Monochrome
- **覆盖**: Tonal contrast, texture emphasis, B&W conversion, film simulation, Ansel Adams zone system, minimalism

### 15. Photo Editing Software (后期软件)
- **标题**: From Good to Extraordinary
- **覆盖**: Lightroom workflow, Photoshop essentials, Capture One, free alternatives, presets, AI editing tools

### 16. Photography Business (摄影商业)
- **标题**: Turn Passion into Profit
- **覆盖**: Pricing strategies, portfolio building, marketing, client contracts, print sales, workshop hosting

### 17. Social Media Photography (社媒摄影)
- **标题**: Stand Out in the Feed
- **覆盖**: Instagram composition, TikTok photo trends, Pinterest strategy, brand collaboration, content planning, analytics

## 图片清单

| 类型 | 数量 | 来源 |
|------|------|------|
| 文章封面 | 30 | Unsplash (photography/camera/landscape) |
| OG默认图 | 1 | 品牌色底+logo |

**Unsplash搜索关键词**: camera photography, photographer shooting, landscape photography, camera lens, photo studio lighting, portrait photography, nature photography, camera gear, tripod setup, photo editing

**注**: Unsplash上摄影主题图片质量极高（都是摄影师上传），是本赛道最大优势。

## 首页区块

1. **Hero**: 深灰蓝底 + "Capture the World Through Your Lens"
2. **Featured Categories**: 5分类卡片
3. **Latest Articles**: 6篇
4. **Quick Tips**: 摄影小技巧横幅
5. **AdSense**: 3个广告位

## 文章结构 (1000-1500字/篇)

三段式。器材评测类含对比表。拍摄技巧类含设置参数建议。每分类6篇。

## CTR与流量增长策略

### 标题优化
- "The Exposure Triangle Explained: Aperture, Shutter Speed & ISO for Beginners"
- "10 Composition Rules That Will Transform Your Photography"
- 含具体相机设置参数增加专业性

### Meta Description
- 具体技能 + 可见成果
- 例: "Master the exposure triangle in 15 minutes. Learn how aperture, shutter speed, and ISO work together with real photo examples and cheat sheets."

### Featured Snippet
- 相机设置参数表进table snippet
- "What is the rule of thirds?" → 40-60字定义 + 示意图描述
- 步骤类(构图/打光)用有序列表

### 内链策略
- 相机基础↔构图↔用光↔后期形成学习路径
- 器材评测→链接到相关拍摄技巧文章
- Related Articles + Read Next

### 内容新鲜度
- 器材评测标注评测年份和固件版本
- 后期软件教程标注软件版本
- 年度 "Best Cameras of 2026" 类型文章(年初更新)

### 回访机制
- 内容系列: "Photography Basics Series (Part 1-6)"
- 打印友好: 设置参数速查表可打印

### 富文本摘要
- FAQ Schema
- HowTo Schema (拍摄步骤)
- Review Schema (器材评测)
- **ImageObject Schema**: 图片页面加ImageObject结构化数据，进Google Images富文本

## 质量与UX标准

### 内容质量
- 每篇文章 ≥1200字，拍摄技巧类含相机设置参数(ISO/光圈/快门)
- 文章结构: 导语钩子 → ToC → Key Takeaways → 正文3段 → 设置速查表 → FAQ → 结论
- 阅读时间标注 + 最后更新日期
- 禁止AI cliché
- 相机设置数据需准确(可验证)，器材评测注明"based on specs comparison"

### 视觉质量
- **图片质量最高优先级** — 摄影站受众对画质敏感，封面图必须高分辨率
- 封面图16:9，lazy loading，alt文本描述拍摄场景
- 深灰蓝`#1E293B`在浅灰底`#F1F5F9`上对比度通过WCAG AA
- 样片对比: Before/After并排，CSS grid 2列
- 禁止图片阴影遮罩(摄影作品不能有任何遮罩)

### UX设计
- 面包屑 + 文章ToC(桌面sticky) + 相关文章(3篇) + 返回顶部 + 阅读进度条
- 移动端纯CSS汉堡菜单
- **相机设置卡片**: 代码块风格(`<pre>`或信息框)，ISO/光圈/快门三要素突出显示
- **构图示意**: 九宫格叠加线(CSS grid 3x3虚线)，展示构图规则
- 图片点击放大: 纯CSS `:target` modal，无JS

### SEO
- Schema: Article + BreadcrumbList + Organization + WebSite + FAQ + (器材评测加Review)
- **图片SEO**: 所有图片alt文本含关键词，文件名语义化(如 `rule-of-thirds-composition.jpg`)
- Image Sitemap 或 sitemap.xml 中含图片URL
- Meta/OG/Twitter/Canonical 完整
- 内部链接每篇2-3个

### 广告位
- 3个/篇，纯自动广告，禁止手动广告位

### 性能
- 预连接 + lazy loading + 零JS
- **图片优化重点**: 摄影站图片多，PIL压缩必须quality=85以下，max_width=1200
- 响应式图片: `<img srcset="..." sizes="...">` 提供2x版本给Retina屏幕

### 无障碍
- 语义化HTML + Skip to content + img有alt(摄影站尤其重要) + 键盘可导航

## 实现步骤

**执行前必读: `specs/MANDATORY_RULES.md`** — 所有强制规定必须在每个阶段逐条对照。

1-9步流程。CF项目名: photography-jycsd。

## 验收标准

```bash
ls sub-photography/article-*.html | wc -l                # >= 102
ls sub-photography/category-*.html | wc -l               # >= 17
grep -c 'article-card' sub-photography/index.html        # >= 6
python shared/pre_commit_audit.py
python shared/check_portal_consistency.py
python shared/health_check_daily.py --quality
python shared/refresh_sitemap.py sub-photography
```

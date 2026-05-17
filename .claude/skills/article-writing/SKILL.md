---
name: article-writing
description: AdSense英文矩阵站文章生成 — 1000-1500字，三段式，Tailwind HTML，3广告位
origin: ECC (定制版)
---

# Jycsd 矩阵站文章生成

为 6 个 AdSense 子站生成纯静态 HTML 英文文章，每篇 1000-1500 字，Tailwind CSS CDN。

## 站点主题
| 子站 | 目录 | 主题 | 品牌色 |
|------|------|------|--------|
| healthy-jycsd | sub-healthy | 健康饮食 | 绿 green-600 |
| pets-jycsd | sub-pets | 宠物护理 | 橙 orange-600 |
| home-jycsd | sub-home | 家居园艺 | 鼠尾草绿 emerald-700 |
| finance-jycsd | sub-finance | 个人理财 | 蓝 blue-700 |
| tech-jycsd | sub-tech | 科技数码 | 灰蓝 slate-700 |
| travel-jycsd | sub-travel | 旅行攻略 | 青 cyan-700 |

## 文章结构（三段式）
1. **核心要点** (2-3段落): 问题/场景引入 + 文章价值概述
2. **细分讲解** (4-6个h2段落): 每个要点深入展开
3. **场景应用** (1-2段落): 实际场景 + 总结建议

## HTML 模板要求
- `<head>` 必须包含:
  - AdSense Auto Ads script (`pagead2.googlesyndication.com/pagead/js/adsbygoogle.js`)
  - `<meta name="google-adsense-account" content="ca-pub-2595917642864488">`
  - `<meta name="description">` (120-155字符)
  - `<meta property="og:title">` and `<meta property="og:description">`
  - `<link rel="canonical">` with full URL
  - GA4 script (`G-GGNWR1X1GV`)
  - Tailwind CDN + Roboto font
  - NewsArticle + BreadcrumbList JSON-LD Schema
- `<body>` 必须包含:
  - 站点头部 nav (品牌名 + 导航链接)
  - 文章标题 h1 + 作者信息 + 日期 + 封面图
  - `<div class="article-content">` 内: 3 个 ad-unit + h2 标题 + 内容
  - 侧边栏 "Recent Posts" (链接其他文章)
  - 站点头部 footer (版权 + 导航)

## 广告位格式（3个，按顺序插入h2后）
```html
<div class="ad-unit">
<span class="ad-label">Advertisement</span>
<ins class="adsbygoogle" style="display:block; min-height:280px" data-ad-client="ca-pub-2595917642864488" data-ad-slot="9112825459" data-ad-format="auto" data-full-width-responsive="true"></ins>
<script>(adsbygoogle = window.adsbygoogle || []).push({});</script>
</div>
```
Slot 顺序: 9112825459 (top), 4397738132 (mid), 9739511410 (bottom)

## 写作要求
- 字数: 1000-1500 英文单词
- 段落: 每段 3-5 句话，行间距 1.8
- 标题: h2 至少 4 个，可加 h3 子标题
- 列表: 用 `<ul>` / `<ol>` 增加可读性
- 引用: 用 `<blockquote>` 突出关键数据/建议
- 风格: 专业权威，有数据支撑，实用建议
- 禁止: emoji、虚词、废话、AI味
- 目标受众: 美国普通消费者

## 文件命名
- 格式: `article-N.html`（N 为下一个可用编号）
- URL: `https://<子域名>.jycsd.com/article-N.html`

## 新文章 checklist
- [ ] 审核通过: `python d:/AI网站文件夹/shared/pre_commit_audit.py`
- [ ] 更新 index.html 侧边栏 Recent Posts
- [ ] 更新 sitemap.xml
- [ ] 更新首页文章列表（如有）

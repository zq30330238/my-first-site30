# Schema JSON-LD 注入规范

## 目标
所有页面注入 JSON-LD 结构化数据，提升搜索结果的富文本摘要展示。

## Schema 类型

### 文章页（所有 article-*.html）
注入两个 JSON-LD 块在 `</head>` 之前：

**1. Article Schema**
```json
{
  "@context": "https://schema.org",
  "@type": "NewsArticle",
  "headline": "<从 <title> 提取>",
  "description": "<从 meta description 提取>",
  "author": {"@type": "Person", "name": "<从作者区提取>"},
  "datePublished": "<从日期提取，ISO格式>",
  "dateModified": "<同 datePublished>",
  "publisher": {
    "@type": "Organization",
    "name": "<站点名，如 PetCare Hub>",
    "url": "https://<子域名>.jycsd.com"
  },
  "mainEntityOfPage": {"@type": "WebPage", "@id": "<文章完整URL>"}
}
```

**2. BreadcrumbList Schema**
```json
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {"@type": "ListItem", "position": 1, "name": "Home", "item": "<首页URL>"},
    {"@type": "ListItem", "position": 2, "name": "<分类名>", "item": "<分类URL>"},
    {"@type": "ListItem", "position": 3, "name": "<文章标题>"}
  ]
}
```

### 首页（index.html）
注入 Organization + WebSite Schema。

## 各站点域名映射
| 目录 | 域名 | 站点名 | 主色 |
|------|------|--------|------|
| main-site | jycsd.com | 江阴车速递 | #1e3a5f |
| sub-healthy | healthy.jycsd.com | HealthyEats | #16a34a |
| sub-pets | pets.jycsd.com | PetCare Hub | #f97316 |
| sub-home | home.jycsd.com | HomeJoy | #84cc16 |
| sub-finance | finance.jycsd.com | MoneyWise | #1e40af |
| sub-tech | tech.jycsd.com | TechNest | #64748b |
| sub-travel | travel.jycsd.com | TripRoute | #0891b2 |

## 实现方式
用 Python 脚本批量注入，脚本需：
- 遍历所有 sub-*/article-*.html 和 index.html
- 从 HTML 中正则提取标题、描述、作者、日期、分类
- 生成对应的 JSON-LD <script> 块
- 注入到 `</head>` 之前
- 已注入过的文件跳过（检测 `application/ld+json`）

# AGENTS.md — Codex 项目指令

## 项目概况
JYCSD 英文内容站矩阵，7站纯静态HTML+Tailwind CSS CDN，Cloudflare Pages部署。

## 目录结构
```
main-site/      → www.jycsd.com（品牌主站，海蓝）
sub-healthy/    → healthy.jycsd.com（健康饮食，绿）
sub-pets/       → pets.jycsd.com（宠物护理，橙）
sub-home/       → home.jycsd.com（家居园艺，鼠尾草绿）
sub-finance/    → finance.jycsd.com（个人理财，蓝）
sub-tech/       → tech.jycsd.com（科技数码，灰蓝）
sub-travel/     → travel.jycsd.com（旅行攻略，青）
shared/         → 公共脚本和工具
```

## 技术栈
- 纯静态HTML，零JS框架（仅Tailwind CSS CDN）
- 字体: Roboto/Arial, 正文≥16px, 行距1.5
- URL: `/article-name.html` 扁平结构
- 每文1000-1500字，三段式: 核心要点→细分讲解→场景应用
- SEO: JSON-LD Schema (NewsArticle), OG标签, canonical, robots.txt, sitemap.xml
- AdSense: 每页2-3个广告位

## 禁止
- 禁止添加JS框架/构建工具
- 禁止引入emoji到页面内容
- 禁止改其他子站文件（每个子站独立）
- 禁止创建README/文档（除非明确要求）

## 部署流程
```
改文件 → git add → git commit → git push → Cloudflare Pages自动部署
或: npx wrangler pages deploy <dir> --project-name=<project> --branch=master
```

## 各子站Pages项目名
| 目录 | 项目名 |
|------|--------|
| main-site | main-site |
| sub-healthy | healthy-jycsd |
| sub-pets | pets-jycsd |
| sub-home | home-jycsd |
| sub-finance | finance-jycsd |
| sub-tech | tech-jycsd |
| sub-travel | travel-jycsd |

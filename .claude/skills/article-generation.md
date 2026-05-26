---
name: article-generation
description: 批量生成英文SEO文章 → 审计 → 部署到Cloudflare Pages。6子站矩阵自动化内容生产。
version: 1.0.0
source: git-history-analysis
---

# 文章批量生成与部署

## 工作流

1. **生成文章**: `python shared/create_articles.py --per-site 5` 在恒创服务器无人值守运行
2. **审计**: `python shared/pre_commit_audit.py` 检查 ad slot、meta 标签、死链
3. **部署**: wrangler pages deploy 每个子站，不能用 git push（Direct Upload 模式）
4. **验证**: fetch 线上 URL 确认 200 OK

## 子站映射

| 目录 | 域名 | project-name |
|------|------|-------------|
| sub-healthy | healthy.jycsd.com | healthy-jycsd |
| sub-pets | pets.jycsd.com | pets-jycsd |
| sub-home | home.jycsd.com | home-jycsd |
| sub-finance | finance.jycsd.com | finance-jycsd |
| sub-tech | tech.jycsd.com | tech-jycsd |
| sub-travel | travel.jycsd.com | travel-jycsd |

## 部署命令

```bash
# Ensure CLOUDFLARE_API_TOKEN is set in environment (read from env var, NOT hardcoded)
export CLOUDFLARE_API_TOKEN="$CLOUDFLARE_API_TOKEN"
npx wrangler pages deploy <目录> --project-name=<项目名> --commit-dirty=true
```

## 关键规则
- 纯静态 HTML，Tailwind CDN，零 JS 依赖
- 每篇 1000-1500 词，3 个 ad unit（h2 #1、#3、#5 后）
- 禁止 emoji，欧美极简风
- 每次部署后必须 fetch 验证线上
